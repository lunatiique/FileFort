import React from "react";
import { Menu, Image } from "semantic-ui-react";
import { Link } from 'react-router-dom';  
import './components.css';

const Header = () => {
  return (
    <Menu className="sticky-header" style={{ marginTop: "10px" }}>
      <Link to="/">
        <Image src="logo512.png" alt="logo" className="iconImg"/>
      </Link>
      <Menu.Menu position="right">
        <Link to="/user/login">
          <a className="item">Login</a>
        </Link>
        <Link to="/cipher/encode">
          <a className="item">Encode</a>
        </Link>
        <Link to="/user/register">
          <a className="item">Register</a>
        </Link>
      </Menu.Menu>
    </Menu>
  );
};

export default Header;
