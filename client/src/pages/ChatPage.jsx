// import React from 'react'
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Chat from '../components/Chat';

const ChatPage = () => {
  const location = useLocation();
  const data = location.state;
  // console.log(data.bot._id)
  const botId = data.bot._id
  const user_email = "kumarvijay2003.vk@gmail.com"
  const [userChat, getUserChat] = useState(null);
  const [botData, setBotData] = useState(null);
  const [loadingChat, setLoadingChat] = useState(true);
  const [loadingBot, setLoadingBot] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    // Fetch chat data from API
    const fetchChatData = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/show_chat/?email=${user_email}&bot_id=${botId}`
        );

        if (!response.ok) {
          throw new Error('Failed to fetch chat data');
        }

        const Chat_data = await response.json();
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

        const response = await fetch(`http://127.0.0.1:8000/get_bot_by_id/?bot_id=${botId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch bot data');
        }

        const botDataResponse = await response.json();
        setBotData(botDataResponse);
        console.log("Bot Data:", botDataResponse);
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
        <div className=" mx-auto pt-20 px-6">

            <Chat data={{userChat,botData}}/>
        </div>
    </>
  )
}

export default ChatPage
