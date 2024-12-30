import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { Button, Icon, Message, Segment } from "semantic-ui-react";

const ImportPrivateKey = () => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");

  // Configure react-dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/x-pem-file": [".pem"], // MIME type for .pem files
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setFile(acceptedFiles[0]);
      setUploadStatus("");
      sessionStorage.removeItem("privateKey");
    },
  });

  // Handle file processing
  const handleFileProcessing = async () => {
    if (!file) {
      setUploadStatus("Please select a file first!");
      return;
    }

    try {
      const fileContent = await file.text(); // Read the file content

      if (!fileContent.includes("-----BEGIN PRIVATE KEY-----")) {
        setUploadStatus("The file does not appear to be a valid private key.");
        return;
      }

      sessionStorage.setItem("privateKey", fileContent); // Store in session
      setUploadStatus("Private key stored successfully in session storage.");
    } catch (error) {
      console.error("Error processing file:", error);
      setUploadStatus("Failed to process the file.");
    }
  };

  // Handle file deletion
  const handleDelete = () => {
    setFile(null);
    setUploadStatus("");
    sessionStorage.removeItem("privateKey");
  };

  return (
    <Segment placeholder style={{ marginTop: "100px" }}>
      <div
        {...getRootProps()}
        style={{
          border: "2px dashed #5AE4A7",
          padding: "20px",
          textAlign: "center",
          borderRadius: "10px",
          cursor: "pointer",
        }}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the private key file here...</p>
        ) : file ? (
          <Message info>
            <Icon name="file" /> {file.name} ({(file.size / 1024).toFixed(2)} KB)
            <Button
              icon="trash"
              color="red"
              size="mini"
              floated="right"
              onClick={(e) => {
                e.stopPropagation(); // Prevent triggering dropzone click
                handleDelete();
              }}
              style={{ marginLeft: "10px" }}
            />
          </Message>
        ) : (
          <p>
            Drag and drop a private key file here, or click to select one.  
            <Icon name="key" />
          </p>
        )}
      </div>

      <Button
        color="teal"
        onClick={handleFileProcessing}
        disabled={!file}
        style={{ marginTop: "20px" }}
      >
        <Icon name="lock" /> Import Private Key
      </Button>

      {uploadStatus && (
        <Message
          success={uploadStatus.includes("successfully")}
          error={uploadStatus.includes("failed") || uploadStatus.includes("not")}
          style={{ marginTop: "20px" }}
        >
          {uploadStatus}
        </Message>
      )}
    </Segment>
  );
};

export default ImportPrivateKey;
