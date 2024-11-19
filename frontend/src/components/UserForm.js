import React, { useState } from 'react';
import { Form, Input, Button, Message, Container, Header } from 'semantic-ui-react';
import './components.css';

function UserForm() {
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:5000/api/create_user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ type: 'success', content: data.message });
      } else {
        setMessage({ type: 'error', content: data.error });
      }
    } catch (error) {
      setMessage({ type: 'error', content: "An error occurred while creating the user." });
    }
  };

  return (
    <Container style={{ marginTop: '30px' }}>
      <Header as="h2" textAlign="center" style={{ marginBottom: '20px' }}>
        New Account
      </Header>
      <Header as="h4" textAlign="center" style={{ marginBottom: '20px' }} className='subheader'>
        Create your own fort to protect your files.
      </Header>
      
      <Form onSubmit={handleSubmit} size="large" loading={false}>
        <Form.Field>
          <label>Username</label>
          <Input
            icon="user"
            iconPosition="left"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your username"
            required
          />
        </Form.Field>
        
        <Form.Field>
          <label>Password</label>
          <Input
            icon="lock"
            iconPosition="left"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
        </Form.Field>

        <Button fluid size="large" type="submit">
          Create User
        </Button>
      </Form>

      {message && (
        <Message
          color={message.type === 'error' ? 'red' : 'green'}
          content={message.content}
          style={{ marginTop: '20px' }}
        />
      )}
    </Container>
  );
}

export default UserForm;
