import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; 
import  { useAuth } from './UserAuthentification';

const Logout = () => {
    const navigate = useNavigate();  
    const { logout } = useAuth();

    useEffect(() => {
        logout(); // Trigger the logout function to clear the user
        sessionStorage.removeItem('privateKey'); // Remove privateKey from session storage
        navigate('/'); // Redirect to the home page after logout    
    }, [logout, navigate]); // Ensure the effect runs only when `logout` or `history` changes

    return (
        <div>
            <h2>Logging out...</h2>
        </div>
    );
};

export default Logout;