import React, { Component } from "react";
import { Container, Header, Image } from "semantic-ui-react";
import '../components/components.css';

class Home extends Component {
    render () {
        return (
            <Container style={{ marginTop: '30px' }}>
                <Header as="h1" textAlign="center" style={{ marginBottom: '20px' }}>
                    FileFort
                </Header>
                <Header as="h4" textAlign="center" style={{ marginBottom: '20px' }} className='subheader'>
                    Create your own fort to protect your files.
                </Header>
                <Image src="logo512.png" alt="logo" centered className="center-image"/>
                <div className='home-text'>
                    FileFort is a secure file storage service that allows you to store your files in a secure and encrypted environment. 
                    Based on COBRA, finalist of the AES competition, FileFort uses a combination of symmetric and asymmetric encryption to protect your files.
                </div>
            </Container>
        )
    }
}

export default Home;