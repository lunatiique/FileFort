import React, { useState } from 'react';
import { Button, Form, Input, Message } from 'semantic-ui-react';


function GenerateKey() {

    const [key, setKey] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:5000/api/generate_key_128', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            const data = await response.json();
            setKey(data.key);
            setMessage({ type: 'success', content: "Key generated successfully. If you encode text with this key, please store it somewhere to be able to decipher the encoded text." });
        } catch (error) {
            setMessage({ type: 'error', content: "An error occurred while generating a new key" });
        }
        setLoading(false);
    }

    return (
        <div className='element-encode'>
            <Form onSubmit={handleSubmit} size="large" loading={false}>
                <Form.Field>
                    <label>Generate a key</label>
                    <Input
                        icon="key"
                        iconPosition="left"
                        type="text"
                        value={key}
                        onChange={(e) => setKey(e.target.value)}
                        placeholder="Here will be displayed your key"
                    />
                </Form.Field>

                <Button type='submit' fluid size='large' loading={loading}>Generate Key</Button>
            </Form>
            {message && (
                <Message
                    color={message.type === 'error' ? 'red' : 'green'}
                    content={message.content}
                    style={{ marginTop: '20px' }}
                />
            )}
        </div>
    );
}

export default GenerateKey;