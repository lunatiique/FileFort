import React, {useState} from "react";
import { Button, Form, Input, Message } from 'semantic-ui-react';

function EncodeText() {
    const [text, setText] = useState('');
    const [key, setKey] = useState('');
    const [encodedText, setEncodedText] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://127.0.0.1:5000/api/encode_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, key }),
            });
            // While waiting for the response, the loading state is set to true
            // When the response is received, the loading state is set to false
            setLoading(true);
            const data = await response.json();
            setLoading(false);
            setEncodedText(data.encoded_text);
            setMessage({ type: 'success', content: "Text encoded successfully" });
        } catch (error) {
            setMessage({ type: 'error', content: "An error occurred while encoding the text" });
        }
    }

    return(
        <div className="element-encode">
            <Form onSubmit={handleSubmit} size="large" loading={false}>
                <Form.Field>
                    <label>Text</label>
                    <Input
                        icon="file text"
                        iconPosition="left"
                        type="text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Text to encode"
                    />
                </Form.Field>
                <Form.Field>
                    <label>Key</label>
                    <Input
                        icon="key"
                        iconPosition="left"
                        type="text"
                        value={key}
                        onChange={(e) => setKey(e.target.value)}
                        placeholder="Key to encode the text"
                    />
                </Form.Field>
                <Form.Field>
                    <label>Encoded Text</label>
                    <Input
                        icon="lock"
                        iconPosition="left"
                        type="text"
                        value={encodedText}
                        placeholder="Here will be displayed the encoded text"
                        readOnly
                    />
                </Form.Field>
                <Button type='submit' fluid size='large'>Encode Text</Button>
            </Form>
            {message && (
                <Message
                    color={message.type === 'error' ? 'red' : 'green'}
                    content={message.content}
                    style={{ marginTop: '20px' }}
                />
            )}
            {loading && (
                <Message
                    color='blue'
                    content='Loading...'
                    style={{ marginTop: '20px' }}
                />
            )}
        </div>

    )
}

export default EncodeText;