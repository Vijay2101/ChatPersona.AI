import React from 'react'
import SignIn from "../components/SignIn";
import Navbar2 from "../components/Navbar2";

const SignInPage = () => {
  return (
    <>
        <Navbar2 />
      <div className="max-w-7xl mx-auto pt-20 px-6">

        <SignIn />
    
      </div>
    </>
  )
}

export default SignInPage