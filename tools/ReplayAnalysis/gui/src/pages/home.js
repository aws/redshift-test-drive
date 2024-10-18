import Input from "@awsui/components-react/input";
import Button from "@awsui/components-react/button";
import AppLayout from "@awsui/components-react/app-layout";
import React, {useEffect, useState} from "react";
import {Container, FormField, Header, SpaceBetween, TokenGroup} from "@awsui/components-react";
import ReplayList from "../components/ReplayList";
import AccessControl from "../components/AccessControl";

export const HomePage = () => {

    const [resource, setResource] = useState('');
    const [replays, setReplays] = useState([])
    const [workloads, setWorkloads] = useState([])
    const [workloadLabels, setWorkloadLabels] = useState([])
    const [searching, setSearching] = useState(false)
    const [profiles, setProfiles] = useState([])
    const [valid, setValid] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            const response = await fetch(`/getprofile`);
            const newData = await response.json();
            setProfiles(newData.profiles);
        };
        fetchData();
    }, []);

    function search(uri) {
        // TODO: explicit s3 uri validation

        if (uri !== '' && uri.startsWith('s3://')) {
            setSearching(true);

            fetch(`/search?uri=${encodeURIComponent(uri)}`).then(response => response.json())
                .then(response => {
                    if (!response.success) {
                        setValid(false)
                    } else {
                        if (!workloads.includes(response.workload)) {
                            setReplays(replays => [...replays, ...response.replays]);
                            setWorkloads(workloads => [...workloads, response.workload]);
                            setWorkloadLabels(workloads => [...workloads, {label: response.workload}]);
                        }
                    }

                    setSearching(false);


                }).catch((error) => {
                console.error('Error:', error);
                setSearching(false);

            });
            setResource("");
        } else {
            setValid(false)

        }
    }

    /**
     * Removes entries from list of replays when workload is removed
     * @param {number} itemIndex Total data set of query frequency values.
     */
    function removeWorkload(itemIndex) {
        let workload = workloadLabels[itemIndex].label
        setWorkloadLabels([...workloadLabels.slice(0, itemIndex),
            ...workloadLabels.slice(itemIndex + 1)]);
        setWorkloads([...workloads.slice(0, itemIndex),
            ...workloads.slice(itemIndex + 1)]);
        let result = replays.filter((data) => {
            return data.workload !== workload;
        });
        setReplays(result);
    }

    return (
        <AppLayout
            navigationHide={true}
            content={
                <Container
                    header={
                        <Header variant="h1" description="An analysis tool provided by Redshift.">
                            Test Drive Replay Analysis
                        </Header>
                    }>
                    <SpaceBetween size={"l"}>
                        <AccessControl profiles={profiles}></AccessControl>


                        <FormField label="Replay analysis file location"
                                   errorText={!valid && "Unable to access S3. Please check the provided URI."}
                                   secondaryControl={
                                       <Button
                                           disabled={resource === ""}
                                           loading={searching}
                                           variant={'primary'}
                                           onClick={() => search(resource)}>
                                           Search
                                       </Button>}>

                            <Input value={resource}
                                   errorText="This is an error message."

                                   type={'search'}
                                   placeholder={"s3://bucket/prefix/object"}
                                   onChange={(event) => {
                                       setResource(event.detail.value);
                                       setValid(true)
                                   }}/>

                        </FormField>

                        <TokenGroup
                            onDismiss={({detail: {itemIndex}}) => {
                                removeWorkload(itemIndex)
                            }}
                            items={workloadLabels}>

                        </TokenGroup>

                        <ReplayList search={searching} replays={replays}/>

                    </SpaceBetween>


                </Container>
            }

        />
    );

}

