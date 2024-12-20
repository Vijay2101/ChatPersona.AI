import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom'; // Hook to get current location
import { useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import FeatureSection from '../components/FeatureSection';
import Workflow from '../components/Workflow';
import Pricing from '../components/Pricing';
import Testimonials from '../components/Testimonials';
import Footer from '../components/Footer';
import ChatBotsList from '../components/ChatBotsList';
import ChatBotDesc from '../components/ChatBotDesc';
import ChatBotDesc2 from '../components/ChatBotDesc2';

const ChatbotPage = () => {
    const [botData, setBotData] = useState(null); // State to store the fetched data
    const location = useLocation();
    console.log(location.search)
    const queryParams = new URLSearchParams(location.search);
    console.log(queryParams)
    const botId = queryParams.get('bot_id');
    // Fetch data from the API
    useEffect(() => {
        const fetchBotData = async () => {
        try {
            // Check if botData is already available or botId is the same
            if (botData ) {
                return; // Avoid fetching again if the botData is already loaded and matches
            }
            // Get bot_id from the query string using URLSearchParams
            
            const response = await fetch(`https://chat-persona-ai-ov46.vercel.app/get_bot_by_id/?bot_id=${botId}`);
            const data = await response.json();
            setBotData(data); // Set the fetched data into state
            console.log(data.bot.bot_name)
        } catch (error) {
            console.error("Error fetching bot data:", error);
        }
        };
    
        fetchBotData();
    }, []); // Dependency array ensures the effect runs when the botId changes
    
    // Render loading state while fetching data
    if (!botData) {
        return <div>Loading...</div>;
    }

    return (
        <>
            <div className=" mx-auto pt-20 px-6  bg-gradient-to-b from-orange-500/35">

                <ChatBotDesc data={botData} />
            </div>
            <div className=" mx-auto pt-20 px-6  ">

                <ChatBotDesc2 data={botData} />
                <Footer />
            </div>
        </>
    );
};

export default ChatbotPage;
