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
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
