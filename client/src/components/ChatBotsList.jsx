import React, { useState, useEffect } from 'react';
// import { Chatbots } from "../constants";
import { Link } from 'react-router-dom';
// bot_name
// description
// image_url
// start_message
const ChatBotsList = () => {
    const wordLimit = 30; // Adjust this value to control the number of words shown
    const [chatbots, setChatbots] = useState([]);
    
    
    useEffect(() => {
        const fetchChatbots = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/get_all_bots');
                const data = await response.json();
                setChatbots(data.bots);  // Update the state with the fetched data
                console.log(data)
            } catch (error) {
                console.error('Error fetching chatbots data:', error);
            }
        };

        fetchChatbots();
    }, []);
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
