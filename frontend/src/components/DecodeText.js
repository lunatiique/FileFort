import React, {useState} from "react";
import { Button, Form, Input, Message } from 'semantic-ui-react';

function DecodeText() {
    const [text, setText] = useState('');
    const [key, setKey] = useState('');
    const [decodedText, setDecodedText] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:5000/api/decode_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, key }),
            });
            const data = await response.json();
            setDecodedText(data.decoded_text);
            setMessage({ type: 'success', content: "Text decoded successfully" });
        } catch (error) {
            setMessage({ type: 'error', content: "An error occurred while decoding the text" });
        }
        setLoading(false);
    }

    return(
        <div className="element-encode-last">
            <Form onSubmit={handleSubmit} size="large" loading={false}>
                <Form.Field>
                    <label>Text</label>
                    <Input
                        icon="lock"
                        iconPosition="left"
                        type="text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Text to decode"
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
                        placeholder="Key to decode the text"
                    />
                </Form.Field>
                <Form.Field>
                    <label>Decoded Text</label>
                    <Input
                        icon="file text"
                        iconPosition="left"
                        type="text"
                        value={decodedText}
                        placeholder="Here will be displayed the decoded text"
                        readOnly
                    />
                </Form.Field>
                <Button type='submit' fluid size='large' loading={loading}>Decode Text</Button>
            </Form>
            {message && (
                <Message
                    color={message.type === 'error' ? 'red' : 'green'}
                    content={message.content}
                    style={{ marginTop: '20px' }}
                />
            )}

        </div>

    )
}

export default DecodeText;