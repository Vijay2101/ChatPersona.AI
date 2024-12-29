import React, { useState, useEffect } from 'react';
import axios from '../axiosInstance'; // Axios setup for HTTP requests

// import { Chatbots } from "../constants";
import { Link } from 'react-router-dom';


const ChatBotsList = () => {
    const wordLimit = 30; // Adjust this value to control the number of words shown
    const [chatbots, setChatbots] = useState([]);
    const [loadingBot, setLoadingBot] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchChatbots = async () => {
            try {
                const response = await axios.get('https://chat-persona-ai-ov46.vercel.app/get_all_bots');
                // console.log(response.data)
                // const data = await response.json();
                const data = response.data
                setChatbots(data.bots);  // Update the state with the fetched data
                console.log(data)
            } catch (err) {
                setError(err.message);
            } finally {
                setLoadingBot(false);
              }
        };

        fetchChatbots();
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
                ChatBots
            </h2>
            <div className="flex flex-wrap">
                {chatbots.map((bot, index) => (
                <div key={index} className="w-full sm:w-1/2 lg:w-1/3 p-2">
                    <div className="p-1 border border-neutral-700 rounded-xl">
                        
                        <div className="flex justify-center items-center">
                            <img
                                className="w-20 h-20 rounded-full border border-neutral-300"
                                src={bot.image_url}
                                alt=""
                            />
                        </div>
                        
                        <p className="text-3xl mb-8 text-center">
                            {bot.bot_name}
                        </p>
                        <p className="text-md text-neutral-500 text-center">
                        {bot.description.split(' ').slice(0, wordLimit).join(' ') + (bot.description.split(' ').length > wordLimit ? '...' : '')}
                        </p>
                    
                        <div className="flex justify-center mt-4">
                            <Link
                                to={`/chatbot/?bot_id=${bot._id}`}
                                className="inline-flex justify-center items-center text-center w-36 h-12 p-3 tracking-tight text-lg hover:bg-orange-900 border border-orange-900 rounded-lg transition duration-200"
                            >
                                Start Chat
                            </Link>
                        </div>
                    </div>
                </div>
                ))}
            </div>
        </div>
    )
}

export default ChatBotsList
