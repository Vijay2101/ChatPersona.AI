import React, { useState, useEffect } from 'react';
import axios from '../axiosInstance'; // Axios setup for HTTP requests

// import { Chatbots } from "../constants";
import { Link } from 'react-router-dom';


const ChatList = () => {
    const wordLimit = 30; // Adjust this value to control the number of words shown
    const [chats, setChats] = useState([]);
    const [loadingBot, setLoadingBot] = useState(true);
    const [error, setError] = useState(null);
    const email = localStorage.getItem('email');
    useEffect(() => {
        const fetchChats = async () => {
            try {
                const response = await axios.get(`https://chat-persona-ai-ov46.vercel.app/get_user_chats/?email=${email}`);
                // console.log(response.data)
                // const data = await response.json();
                const data = response.data
                setChats(data.chats);  // Update the state with the fetched data
                console.log(data)
            } catch (err) {
                setError(err.message);
            } finally {
                setLoadingBot(false);
              }
        };

        fetchChats();
    }, []);


    // Handle loading and errors
  if (loadingBot) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  
  }
    // const truncatedDescription = bot.description.split(' ').slice(0, wordLimit).join(' ') + (bot.description.split(' ').length > wordLimit ? '...' : '');
    return (
        <div className="">
            <h2 className="text-3xl sm:text-5xl lg:text-6xl text-center my-5 tracking-wide">
                Chats
            </h2>
            <div className="flex flex-wrap">
                {chats.map((bot, index) => (
                <div key={index} className="w-full  p-2">
                    <div className="p-1 border border-neutral-700 rounded-xl">
                        
                        <div className="flex p-2 items-center space-x-1">
                            <img
                                className="w-12 h-12 rounded-full border border-neutral-300"
                                src={bot.image_url}
                                alt=""
                            />
                            <div>
                                <p className="text-xl  ">
                                    {bot.bot_name}
                                </p>
                                <span className="text-md text-neutral-500 text-center">{bot.chat_history.split(' ').slice(0, wordLimit).join(' ') + (bot.chat_history.split(' ').length > wordLimit ? '...' : '')}</span>

                            </div>
                            
                            
                        </div>
                        {/* <div>
                            <p className="text-md text-neutral-500 text-center">
                                {bot.chat_history.split(' ').slice(0, wordLimit).join(' ') + (bot.chat_history.split(' ').length > wordLimit ? '...' : '')}
                            </p>
                        </div> */}



                        <div className="flex justify-center mt-4">
                            <Link
                                to={`/chatbot/?bot_id=${bot.bot_id}`}
                                className="mr-4 inline-flex justify-center items-center text-center w-36 h-12 p-3 tracking-tight text-lg hover:bg-orange-900 border border-orange-900 rounded-lg transition duration-200"
                            >
                                Resume Chat
                            </Link>
                            <Link
                                to={`/chatbot/?bot_id=${bot.bot_id}`}
                                className="inline-flex justify-center items-center text-center w-36 h-12 p-3 tracking-tight text-lg hover:bg-orange-900 border border-orange-900 rounded-lg transition duration-200"
                            >
                                Delete
                            </Link>
                        </div>
                    </div>
                </div>
                ))}
            </div>
        </div>
    )
}

export default ChatList
