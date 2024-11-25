import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { Button, Icon, Message, Progress, Segment } from "semantic-ui-react";
import axios from "axios";

const Upload = () => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);

  // Configure react-dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "text/plain": [".txt"],
      "image/x-portable-graymap": [".pgm"], // MIME type for .pgm files
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setFile(acceptedFiles[0]);
      setUploadStatus("");
      setUploadProgress(0);
    },
  });

  // Handle file upload
  const handleUpload = async () => {
    if (!file) {
      setUploadStatus("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://localhost:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });
      setUploadStatus("File uploaded successfully!");

      // Reset progress after a short delay
      setTimeout(() => {
        setUploadProgress(0);
      }, 2000);
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploadStatus("File upload failed.");

      // Reset progress after a short delay
      setTimeout(() => {
        setUploadProgress(0);
      }, 2000);
    }
  };

  // Handle file deletion
  const handleDelete = () => {
    setFile(null);
    setUploadStatus("");
    setUploadProgress(0);
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
          <p>Drop the file here...</p>
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
            Drag and drop a file here, or click to select one.  
            <Icon name="cloud upload" />
          </p>
        )}
      </div>

      {uploadProgress > 0 && (
        <Progress
          percent={uploadProgress}
          indicating
          style={{ marginTop: "20px" }}
        />
      )}

      <Button
        color="teal"
        onClick={handleUpload}
        disabled={!file}
        style={{ marginTop: "20px" }}
      >
        <Icon name="upload" /> Upload File
      </Button>

      {uploadStatus && (
        <Message
          success={uploadStatus.includes("successfully")}
          error={uploadStatus.includes("failed")}
          style={{ marginTop: "20px" }}
        >
          {uploadStatus}
        </Message>
      )}
    </Segment>
  );
};

export default Upload;
