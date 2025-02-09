// import React from 'react'
import { Menu, X } from "lucide-react";
import logo from '../assets/logo3.png';
import {navItems} from '../constants';
import React, { useState } from 'react';
import { Link, useNavigate} from 'react-router-dom';

const Navbar = () => {
    const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)
    const toggleNavbar = () =>{
        setMobileDrawerOpen(!mobileDrawerOpen)
    }
    // const handleLogout = () => {
    //     localStorage.removeItem('token'); // Remove token from localStorage
    //     window.location.href = '/signin'; // Redirect to signin page
    //   };
    const navigate = useNavigate();
    const handleLogout = (e) => {
        e.preventDefault();
        
        // Clear user data from localStorage (or wherever you store the token)
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('username');
        localStorage.removeItem('email');
        
        // Redirect to login page or home
        navigate('/');
      };
      
  return (
    <nav className="sticky top-0 z-50 py-3 backdrop-blur-lg border-b border-neutral-700/80">
        <div className="container px-4 mx-auto relative lg:text-sm">
            <div className="flex justify-between items-center">
                <div className="flex items-center flex-shrink-0">
  <Link
    to="/"
  >
                    <img src={logo} alt="logo" className="h-10 w-10 mr-2 " />
                    </Link>
                    <Link
    to="/"
  >
                    <span className="text-xl tracking-tight">ChatPersona.AI</span>
                    </Link>
                </div>
                <ul className="hidden lg:flex ml-14 space-x-12">
                    {navItems.map((item, index) => (
                        <li key={index}>
                            <Link to={item.href}>{item.label}</Link>
                        </li>
                    ))}
                </ul>
                <div className="hidden lg:flex justify-center space-x-12 items-center">
                    <Link to="/logout" onClick={handleLogout}  className="py-2 px-3 border rounded-md">Logout</Link>
                    <div className="flex items-center space-x-1">
                        <div>
                            <h6>{localStorage.getItem('username')}</h6>
                            <span className="text-sm font-normal italic text-neutral-600">{localStorage.getItem('email')}</span>
                        </div>
                        <img
                            className="w-8 h-8 rounded-full border border-neutral-300"
                            src="https://waikikispecialistcentre.com.au/wp-content/uploads/2024/01/generic-photo.jpg"
                            alt=""
                        />
                    </div>
                </div>
                <div className="lg:hidden md:flex flex-col justify-end">
                    <button onClick={toggleNavbar}>
                        {mobileDrawerOpen ? <X /> : <Menu />}
                    </button>
                </div>
            </div>
            {mobileDrawerOpen && (
                <div className="fixed right-0 z-20 bg-neutral-900 w-full p-12 flex flex-col justify-center items-center lg:hidden">
                    <ul>
                        {navItems.map((item, index) => (
                            <li key={index} className="py-4">
                                <Link to={item.href}>{item.label}</Link>
                            </li>
                        ))}
                    </ul>
                    <div className="flex space-x-6">
                        <Link to="/signin" className="py-2 px-3 border rounded-md">
                            Logout
                        </Link>
                        
                    </div>
                    <div className="flex items-center space-x-1">
                        <div>
                            <h6>{localStorage.getItem('username')}</h6>
                            <span className="text-sm font-normal italic text-neutral-600">{localStorage.getItem('email')}</span>
                        </div>
                        <img
                            className="w-8 h-8 rounded-full border border-neutral-300"
                            src="https://waikikispecialistcentre.com.au/wp-content/uploads/2024/01/generic-photo.jpg"
                            alt=""
                        />
                    </div>
                </div>
            )}

        </div>

    </nav>
  )
}

export default Navbar
