import React, { Component } from "react";
import { Container, Header } from "semantic-ui-react";
import GenerateKey from "../../components/GenerateKey";
import EncodeText from "../../components/EncodeText";
import DecodeText from "../../components/DecodeText";

class Encode extends Component {
    render () {
        return (
            <Container style={{ marginTop: '30px' }}>
                <Header as="h1" textAlign="center" style={{ marginBottom: '20px' }}>
                    Encode/Decode Text
                </Header>
                <Header as="h4" textAlign="center" style={{ marginBottom: '20px' }} className='subheader'>
                    Test COBRA implementation.
                </Header>
                <GenerateKey/>
                <EncodeText />
                <DecodeText />
            </Container>
        )
    }
}

export default Encode;