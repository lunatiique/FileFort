// src/App.js
import React from 'react';
import Register from './pages/user/register';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Layout from './components/Layout';
import Home from './pages/home.js';
import Encode from './pages/cipher/encode';
import Login from './pages/user/login';
import LogoutPage from './pages/user/logout';
import UploadFile from './pages/user/uploadFile';
import DownloadFile from './pages/user/downloadFile';
import PrivateKeyPage from './pages/user/privateKey';
import Simulate from './pages/cipher/simulateCommunication.js';

function App() {
  

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/user/register" element={<Register/>} />
          <Route path="/cipher/encode" element={<Encode/>} />
          <Route path="/user/login" element={<Login/>} />
          <Route path="/user/logout" element={<LogoutPage/>} />
          <Route path="user/uploadFile" element={<UploadFile/>} />
          <Route path="user/downloadFile" element={<DownloadFile/>} />
          <Route path="user/privateKey" element={<PrivateKeyPage/>} />
          <Route path="cipher/simulateCommunication" element={<Simulate/>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
