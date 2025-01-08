import React, { useState } from "react";
import { Button, Container, Segment, List } from "semantic-ui-react";

// Function to format the current time as [Wed. 8 Jan. 2025 14:50:33]
const getFormattedTime = () => {
    const now = new Date();
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
    return now.toLocaleString('en-US', options);
};

const SimulationTerminal = () => {
    const [messages, setMessages] = useState([]);
    const [isRunning, setIsRunning] = useState(false);
    const [eventSource, setEventSource] = useState(null);

    const startSimulation = async () => {
        // Set up the event stream when the button is clicked
        const es = new EventSource('http://localhost:5000/api/simulation');

        es.onmessage = (event) => {
            // Add timestamp before each message
            const timestamp = getFormattedTime();
            const message = `[${timestamp}] $ :- ${event.data}`;
            setMessages((prevMessages) => [...prevMessages, message]);
        };

        es.onerror = (error) => {
            console.error("Error in EventSource connection:", error);
            es.close();
        };

        setEventSource(es);
        // Prevent multiple connections
        setIsRunning(true);
    };

    const stopSimulation = () => {
        if (eventSource) {
            eventSource.close(); // Stop the event stream
        }
        setMessages([]); // Clear all messages
        setIsRunning(false); // Update the button state
    };

    return (
        <Container style={{ marginTop: '20px' }}>
            <Segment>
                <h2>Simulation Progress</h2>
                <Button
                    primary
                    onClick={startSimulation}
                    disabled={isRunning}
                    style={{ marginBottom: '10px' }}
                >
                    {isRunning ? 'Simulation in Progress...' : 'Start Simulation'}
                </Button>
                <Button
                    color="red"
                    onClick={stopSimulation}
                    disabled={!isRunning}
                    style={{ marginBottom: '10px' }}
                >
                    Stop Simulation
                </Button>
                <Segment style={{ height: '400px', overflowY: 'auto', backgroundColor: '#2e2e2e', color: '#fff', fontFamily: 'monospace', padding: '10px' }}>
                    <List divided relaxed>
                        {messages.map((message, index) => (
                            <List.Item key={index} style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                                {message}
                            </List.Item>
                        ))}
                    </List>
                </Segment>
            </Segment>
        </Container>
    );
};


export default SimulationTerminal;
