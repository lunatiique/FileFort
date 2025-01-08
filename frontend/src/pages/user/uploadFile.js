import React, {Component} from "react";
import { Container, Header } from "semantic-ui-react";
import Upload from "../../components/Upload";


class UploadFile extends Component {
    render () {
        return (
            <Container style={{ marginTop: '30px' }}>
                 <Header as="h1" textAlign="center" style={{ marginBottom: '20px' }}>
                    Upload File to your Safe
                </Header>
                <Upload />
            </Container>
        )
    }
}

export default UploadFile;

    