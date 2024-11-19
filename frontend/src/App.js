// src/App.js
import React, { useState } from 'react';
import Register from './pages/user/register';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Layout from './components/Layout';
import Home from './pages/home.js';
import Encode from './pages/cipher/encode';
import Login from './pages/user/login';

function App() {
  

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/user/register" element={<Register/>} />
          <Route path="/cipher/encode" element={<Encode/>} />
          <Route path="/user/login" element={<Login/>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
