// import React from 'react'
import React, { useState, useEffect } from 'react';
import axios from '../axiosInstance'; // Axios setup for HTTP requests
import { useLocation } from 'react-router-dom';
import Chat from '../components/Chat';
import Navbar from "../components/Navbar";

const ChatPage = () => {
  const location = useLocation();
  const data1 = location.state;
  // console.log(data.bot._id)
  const data= data1.key
  console.log(data.bot._id)
  console.log("data aaya kyaaaa")
  const botId = data.bot._id
  const user_email = localStorage.getItem('email')
  const [userChat, getUserChat] = useState(null);
  const [botData, setBotData] = useState(null);
  const [loadingChat, setLoadingChat] = useState(true);
  const [loadingBot, setLoadingBot] = useState(true);
  const [error, setError] = useState(null);
  console.log("aaya22")
  useEffect(() => {
    // Fetch chat data from API
    const fetchChatData = async () => {
      try {
        const response = await axios.get(
          `https://chat-persona-ai-ov46.vercel.app/show_chat/?email=${user_email}&bot_id=${botId}`
        );

        // if (!response.ok) {
        //   console.log("naaaaaa1")
        //   throw new Error('Failed to fetch chat data');
        // }

        const Chat_data =  response.data;
        console.log("*************")
        console.log(Chat_data)
        getUserChat(Chat_data);
        console.log(Chat_data)
      } catch (err) {
        setError(err.message);
      } finally {
        setLoadingChat(false);
      }
    };

    fetchChatData();
  }, [user_email, botId]);

  // Fetch bot data
  useEffect(() => {
    const fetchBotData = async () => {
      try {
        if (botData) {
          return; // Avoid fetching again if bot data is already loaded
        }

        const response = await axios.get(`https://chat-persona-ai-ov46.vercel.app/get_bot_by_id/?bot_id=${botId}`);
        console.log("fun")
        console.log(response)
        // if (!response.ok) {
        //   throw new Error('Failed to fetch bot data');
        // }

        const botDataResponse = await response.data;
        setBotData(botDataResponse);
        console.log("Bot Data:", botDataResponse);
        console.log("fun77")
      } catch (error) {
        console.error("Error fetching bot data:", error);
      } finally {
        setLoadingBot(false);
      }
    };

    fetchBotData();
  }, [botId, botData]);

  // Handle loading and errors
  if (loadingChat || loadingBot) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }



  // console.log(data)
  return (
    <>
        <Navbar />
        <div className=" mx-auto pt-3 px-6">

            <Chat data={{userChat,botData}}/>
        </div>
    </>
  )
}

export default ChatPage
