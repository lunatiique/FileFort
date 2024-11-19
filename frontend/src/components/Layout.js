import React from "react";
import { Container } from "semantic-ui-react";
import Header from "./Header";
import Footer from "./Footer";
const Layout = (props) => {
  return (
    <div>
      <Container>
          <link
            rel="stylesheet"
            href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.css"
          ></link>
        <Header />
        {props.children}
        <Footer />
      </Container>
    </div>
  );
};
export default Layout;
