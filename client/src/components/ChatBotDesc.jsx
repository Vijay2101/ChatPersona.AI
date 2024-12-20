import React from 'react'
import { useNavigate, Link } from 'react-router-dom';
// import { Link } from 'react-router-dom';
import { CheckCircle2 } from "lucide-react";
import codeImg from "../assets/code.jpg";
import { checklistItems } from "../constants";

const ChatBotDesc = ({ data }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    // const data = { key: 'value' }; // Replace with the data you want to send
    console.log("click kar diya")
    console.log(data)
    navigate('/chat', { state: data });
  };
  return (
    <div className="">
      {/* <h2 className="text-3xl sm:text-5xl lg:text-6xl text-center mt-6 tracking-wide">
      Enhance your  {" "}
        <span className="bg-gradient-to-r from-orange-500 to-orange-800 text-transparent bg-clip-text">
        conversational experience
        </span>
        {" "} like never before.
      </h2> */}

        <div className="flex flex-wrap justify-center">
            <div className="p-2 w-full lg:w-1/2 flex flex-col items-center">
                <img 
                    src={data.bot.image_url}
                    alt="Coding" 
                    className="rounded-full border border-neutral-300"
                    style={{
                        width: "20rem", // Base size ~ 96px
                        height: "20rem",
                      }}
                />
                <p className="mt-5 text-3xl mb-8 text-center tracking-wide">
                                {data.bot.bot_name}
                               
                </p>
            </div>
            <div className="pt-12 w-full lg:w-1/2 flex flex-col items-center justify-center">
                <p className='mt-5 tracking-wide'>
                {data.bot.start_message}
                </p>
                <div className="pt-12 w-full lg:w-1/2 flex flex-row items-center justify-center">
            
                    <Link
                        to="/chat"
                        state={{ key: data }}
                        className="bg-gradient-to-r from-orange-500 to-orange-800 py-3 px-4 mx-3 rounded-md w-30"
                        >
                        Chat Now
                        </Link>
                        <Link to="#" className="py-3 px-4 mx-3 rounded-md border ">
                        Add to favourite
                    </Link>

                </div>
            </div>
            
        </div>

        
    </div>
  )
}

export default ChatBotDesc
