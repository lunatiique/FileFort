
import React from 'react';
import Download from '../../components/Download';
import { Container, Header } from "semantic-ui-react";


const DownloadFile = () => {
  return (
    <Container style={{ marginTop: '30px' }}>
      <Header as="h1" textAlign="center" style={{ marginBottom: '20px' }}>
        Download File from your Safe
      </Header>
    <Download/>
    </Container>
  );
};

export default DownloadFile;