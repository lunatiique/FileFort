import React, { useState } from 'react';
import { Form, Input, Button, Message, Container, Header } from 'semantic-ui-react';
import './components.css';
import  { useAuth } from './UserAuthentification';
import { useNavigate } from 'react-router-dom'; 
import ImportPrivateKey from './ImportPrivateKey';

function UserForm() {
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();


  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (!name || !password || !sessionStorage.getItem('privateKey')) {
        setMessage({ type: 'error', content: 'Please fill in all the fields. (Do not forget to click on Import Private Key)' });
        return;
      }
      const response = await fetch('http://127.0.0.1:5000/api/login_user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, password, privateKey: sessionStorage.getItem('privateKey') }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ type: 'success', content: data.message });
        login({name : name})
        //Switch to the home page after delay of 200ms
        setTimeout(() => {
          navigate('/');
        }, 200);

      } else {
        setMessage({ type: 'error', content: data.error });
      }
    } catch (error) {
      setMessage({ type: 'error', content: "An error occurred while login the user." });
    }
  };

  return (
    <Container style={{ marginTop: '30px' }}>
      <Header as="h2" textAlign="center" style={{ marginBottom: '20px' }}>
        Login
      </Header>
      <Header as="h4" textAlign="center" style={{ marginBottom: '20px' }} className='subheader'>
        Go to your fort and  get access to your files.
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

        <ImportPrivateKey />

        <Button fluid size="large" type="submit">
          Login
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
