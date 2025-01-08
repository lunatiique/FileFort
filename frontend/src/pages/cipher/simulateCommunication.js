import React, { Component } from "react";
import { Container, Header } from "semantic-ui-react";
import Simulation from "../../components/Simulation";

class Simulate extends Component {
    render () {
        return (
            <Container style={{ marginTop: '30px' }}>
                <Header as="h1" textAlign="center" style={{ marginBottom: '20px' }}>
                    Simulate communication between User and Safe
                </Header>
                <Simulation />
            </Container>
        )
    }
}

export default Simulate;