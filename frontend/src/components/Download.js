import { useAuth } from "./UserAuthentification";
import React, { useState } from "react";
import { Button, Icon, Segment, Message, Table, Loader } from "semantic-ui-react";

const Download = () => {
    const { user } = useAuth();
    const [listFiles, setListFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchFiles = async () => {
        try {
            setLoading(true);
            const response = await fetch("http://localhost:5000/api/files", {
                headers: {
                    Authorization: user.name,
                },
            });
            if (response.ok) {
                const data = await response.json();
                setListFiles(data.files);
            } else {
                throw new Error("Failed to fetch files");
            }
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async (file) => {
        try {
            setLoading(true);
            const response = await fetch(`http://localhost:5000/api/files/${file.name}?privateKey=${sessionStorage.getItem("privateKey")}`, {
                headers: {
                    Authorization: user.name,
                },
            });
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = file.name;
                a.click();
            } else {
                throw new Error("Failed to download file");
            }
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (fileName) => {
        try {
            setLoading(true);
            const response = await fetch(`http://localhost:5000/api/files/${fileName}`, {
                method: 'DELETE',
                headers: {
                    Authorization: user.name,
                },
            });
            if (response.ok) {
                setListFiles(listFiles.filter(file => file.name !== fileName));  // Remove file from the list after deletion
            } else {
                throw new Error("Failed to delete file");
            }
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Segment placeholder style={{ marginTop: "100px" }}>
            <h2>Download files from your fort</h2>
            {user && sessionStorage.getItem("privateKey") ? (
                <>
                    <Button
                        primary
                        onClick={fetchFiles}
                        loading={loading}
                        disabled={loading}
                    >
                        <Icon name="download" /> Fetch Files
                    </Button>
                </>
            ) : (
                user ? (<Message info> Please add your private key to the session</Message>) : (
                    <Message info>Please log in to view files</Message>)
            )}

            {loading && <Loader active inline="centered" />}

            {error && (
                <Message error>
                    <Message.Header>Error</Message.Header>
                    <p>{error}</p>
                </Message>
            )}

            {listFiles.length === 0 && !loading && !error && (
                <Message info>No files available</Message>
            )}

            <Table celled>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>Name</Table.HeaderCell>
                        <Table.HeaderCell>Date Added</Table.HeaderCell>
                        <Table.HeaderCell>Download</Table.HeaderCell>
                        <Table.HeaderCell>Delete</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>

                <Table.Body>
                    {listFiles.map((file) => (
                        <Table.Row key={file.name}>
                            <Table.Cell>{file.name}</Table.Cell>
                            <Table.Cell>{new Date(file.dateAdded).toLocaleDateString()}</Table.Cell>
                            <Table.Cell>
                                <Button
                                    icon
                                    color="blue"
                                    onClick={() => handleDownload(file)}
                                >
                                    <Icon name="download" />
                                </Button>
                            </Table.Cell>
                            <Table.Cell>
                                <Button
                                    icon
                                    color="red"
                                    onClick={() => handleDelete(file.name)}
                                >
                                    <Icon name="trash" />
                                </Button>
                            </Table.Cell>
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>
        </Segment>
    );
};

export default Download;
