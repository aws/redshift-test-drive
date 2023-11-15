/*Users*/
select 'Users'::text as query_tag,
  usename, 
  null::text as col_placeholder1,
  null::text as col_placeholder2,
  null::text as col_placeholder3,
  'create user ' || quote_ident('IAM' || regexp_substr(usename, '([^IAM:].*)')) || ' password disable;'
FROM pg_user_info u
where usename <> 'rdsdb'
  and usesuper = 'f'
  and usename like 'IAM:%';


/*Add users and groups*/
select 'Add users and groups'::text as query_tag, 
       pg_get_userbyid(grolist[i]) as username,
       groname,
       null::text as col_placeholder1,
       null::text as col_placeholder2,
       'alter group ' || groname || ' add user ' ||
       quote_ident('IAM' || regexp_substr(pg_get_userbyid(grolist[i]), '([^IAM:].*)')) || ';'       
from (SELECT generate_series(1, array_upper(grolist, 1)) AS i, grolist, groname FROM pg_group) temp
where grolist[i] not in (select usesysid from pg_user where usename = 'rdsdb' or usesuper = 't')
  and username like 'IAM:%';


/*Add users to roles */
with data as (
  select quote_ident('IAM' || regexp_substr(user_name, '([^IAM:].*)')) as username,
                role_name  as rolename,
                admin_option as adminOption,
                'user'::text as type
         from svv_user_grants
         where user_name like 'IAM:%'
)
select 'Add users to roles'::text as query_tag,
       username,
       rolename,
       adminOption,
       null::text as col_placeholder1,
       case
           when type = 'user' and adminOption = 'false' then 'grant role ' || rolename || ' to ' || username || ';'
           else 'grant role ' || rolename || ' to ' || username || ' with admin option;' end as query
from data;


/*User configuration*/
select 'User configuration'::text as query_tag,
       usename,
       useconfig[i],
       null::text as col_placeholder1,
       null::text as col_placeholder2,
       'alter user ' || quote_ident('IAM' || regexp_substr(usename, '([^IAM:].*)')) || ' set ' ||
       case
           when split_part(useconfig[i], '=', 1) = 'TimeZone' then split_part(useconfig[i], '=', 1) || '=''' ||
                                                                   split_part(useconfig[i], '=', 2) || ''''
           else useconfig[i] end || ';'
from (SELECT generate_series(1, array_upper(useconfig, 1)) AS i, useconfig, usename
      FROM pg_user
      where usename like 'IAM:%'
        -- and usesuper = 'f'
     ) temp;


/*User profile*/
select 'User profiles'::text as query_tag,
       usename,
         null::text as col_placeholder1,
         null::text as col_placeholder2,
         null::text as col_placeholder3,
       'alter user ' || quote_ident('IAM' || regexp_substr(usename, '([^IAM:].*)')) ||
       decode(usecreatedb, 't', ' createdb', '') ||
       decode(usesuper, 't', ' createuser', '') || nvl(' connection limit ' || useconnlimit, '') ||
       nvl(' valid until ''' || valuntil || '''', '') || ';'
from (SELECT u.usename,
             u.usesysid,
             u.usecreatedb,
             u.usesuper,
             u.useconnlimit,
             decode(valuntil, 'infinity'::abstime, 'infinity', 'invalid'::abstime, null,
                    to_char(valuntil, 'YYYY-MM-DD HH24:MI:SS')) AS valuntil
      FROM pg_user_info u
      where usename like 'IAM:%'
     ) temp;


/*User syslog access*/
select 'syslogaccess'::text as query_tag,
usename,
null::text as col_placeholder1,
null::text as col_placeholder2,
null::text as col_placeholder3,
'alter user ' || quote_ident('IAM:'|| regexp_substr(usename, '([^IAM:].*)')) || decode(syslogaccess,'UNRESTRICTED',' syslog access UNRESTRICTED') || ';' as query_statement
from(
select usename,
        usesysid,
        syslogaccess
from svl_user_info
where usename like 'IAM:%')
where query_statement is not null;


/*privileges on DB*/
SELECT 'privileges on DB'::text as query_tag,
       QUOTE_IDENT(pg_get_userbyid(b.datdba))::text AS objowner,
       null::text                                   AS schemaname,
       QUOTE_IDENT(b.datname)::text                 AS objname,
       'database'::text                             AS objtype,
       array_to_string(b.datacl, ',')::text         AS aclstring
FROM pg_database b
where pg_get_userbyid(b.datdba) like 'IAM:%'
and aclstring is not null;


/*privileges on schema*/
SELECT 'privileges on schema'::text as query_tag,
       QUOTE_IDENT(pg_get_userbyid(b.nspowner))::text AS objowner,
       null::text                                     AS schemaname,
       QUOTE_IDENT(b.nspname)::text                   AS objname,
       'schema'::text                                 AS objtype,
       array_to_string(b.nspacl, ',')::text           AS aclstring
FROM pg_namespace b
where QUOTE_IDENT(b.nspname) not ilike 'pg\_temp\_%' and
pg_get_userbyid(b.nspowner) like 'IAM:%' 
and aclstring is not null;


/*privileges on tables*/
SELECT 'privileges on tables'::text as query_tag,
       QUOTE_IDENT(pg_get_userbyid(b.relowner))::text AS objowner,
       QUOTE_IDENT(trim(c.nspname))::text             AS schemaname,
       QUOTE_IDENT(b.relname)::text                   AS objname,
       'table'::text                                  AS objtype,
       array_to_string(b.relacl, ',')::text           AS aclstring
FROM pg_class b
         join pg_namespace c on b.relnamespace = c.oid
  where pg_get_userbyid(b.relowner) like 'IAM:%'
  and aclstring is not null;


/*privileges on languages*/
SELECT 'privileges on languages'::text as query_tag,
       null::text                     AS objowner,
       null::text                     AS schemaname,
       lanname::text                  AS objname,
       'language'::text               AS objtype,
       array_to_string(b.lanacl, ',') AS aclstring
FROM pg_language b
where lanacl is not null;


/*privileges on functions*/
SELECT 'privileges on functions'::text as query_tag,
       QUOTE_IDENT(pg_get_userbyid(b.proowner))::text                          AS objowner,
       QUOTE_IDENT(trim(c.nspname))::text                                      AS schemaname,
       QUOTE_IDENT(proname) || '(' || oidvectortypes(proargtypes) || ')'::text AS objname,
       'function'::text                                                        AS objtype,
       array_to_string(b.proacl, ',')                                          AS aclstring
FROM pg_proc b
         join pg_namespace c on b.pronamespace = c.oid
where pg_get_userbyid(b.proowner) like 'IAM:%'
and aclstring is not null;


/*default ACL privileges*/
SELECT 'default ACL privileges'::text as query_tag,
       QUOTE_IDENT(pg_get_userbyid(b.defacluser))::text               AS objowner,
       QUOTE_IDENT(trim(c.nspname))::text                             AS schemaname,
       decode(b.defaclobjtype, 'r', 'tables', 'f', 'functions')::text AS objname,
       'default acl'::text                                            AS objtype,
       array_to_string(b.defaclacl, ',')::text                        AS aclstring
FROM pg_default_acl b
         left join pg_namespace c on b.defaclnamespace = c.oid
where pg_get_userbyid(b.defacluser) like 'IAM:%'
and aclstring is not null;