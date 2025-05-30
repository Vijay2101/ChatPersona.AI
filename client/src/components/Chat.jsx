import React, { useState, useEffect,useRef } from 'react';
import '../scrollbar.css';
import { SendHorizontal } from "lucide-react";
import { EllipsisVertical } from "lucide-react";
import { useNavigate, Link } from 'react-router-dom';

// import axios from 'axios';
import axios from '../axiosInstance';
const Chat = ({data}) => {

  // console.log(data); // Access userChat
  // console.log(data.botData); // Access anotherData
  const username = localStorage.getItem('username');
  const email = localStorage.getItem('email');
  // Static messages for now
  const messages1 = [
    { sender: "user", message: "hello" },
    { sender: "user2", message: "hey user" },

  ];
  // const messages = data.chats
  // console.log(data)
  // State for the message input
  const [messages, setMessages] = useState(data.userChat.chats); // Initialize with the initial data

  // State for the message input
  const [message, setMessage] = useState("");
  const chatEndRef = useRef(null); // Reference to the chat container's bottom

  // Handle the change in message input
  const handleChange = (e) => {
    setMessage(e.target.value);
  };

  // Handle sending a message (for now, just log it)
  const handleSendMessage = async () => {
    if (message.trim()) {
      const newMessage = {
        sender: username,  // You can modify this to be dynamic if needed
        message: message
      }
      // Add the new message to the messages array
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      console.log("Message sent: ", message);
      setMessage(""); // Clear the input field after sending
    
      
      try {
        // Form data to send in the POST request
        const formData = new FormData();
        formData.append("email", email); // Replace with actual email
        formData.append("username", username); // Replace with actual username
        formData.append("bot_id", data.botData.bot._id); // Replace with actual bot_id
        formData.append("bot_name", data.botData.bot.bot_name); // Replace with actual bot_name
        formData.append("prompt", data.botData.bot.prompt); // Current message as the prompt
        formData.append("start_message", data.botData.bot.start_message); // First message in chat
        formData.append("last_message",message
        ); // Last message in chat
        // console.log([data.botData.bot._id,data.botData.bot.bot_name,data.botData.bot.prompt,data.botData.bot.start_message,message])
        // Send the POST request
        console.log("ss----------------------------")
        console.log(formData)
        console.log("ss----------------------------")
        const response = await axios.post("https://chat-persona-ai-ov46.vercel.app/chat_generation/", 
          formData,
          {headers: {
            "Content-Type": "multipart/form-data", // Required for form data
          }},
        
        );
        console.log("res----------------------------")
        console.log(response)
        console.log("res----------------------------")
        // if (!response.ok) {
        //   throw new Error("Failed to send message to the API");
        // }
  
        const bot_response = response.data;
        // const bot_response =
        console.log("API Response:", bot_response);
  
        // Optionally, add the bot's response to the chat
        if (bot_response) {
          setMessages((prevMessages) => [
            ...prevMessages,
            bot_response,
          ]);
        }
      } catch (error) {
        console.error("Error posting to API:", error);
      }
    }
  };

  // Function to handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSendMessage(); // Trigger send message function
    }
  };

  // Scroll to the bottom whenever messages change
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]); 
  return (
    <div className="flex items-center justify-center max-h-screen  rounded-xl">
      <div className="w-full max-w-2xl h-[90vh] border  border-neutral-800  bg-neutral-900 rounded-xl shadow-lg flex flex-col ">

      <div className="flex items-center pl-4 pb-2 pt-2 border-b  border-neutral-800 justify-between">
        <div className="flex items-center space-x-1">
            <img
                className="w-10 h-10 rounded-full border border-neutral-300"
                src={data.botData.bot.image_url}
                alt=""
            />
            <div>
                <h6>{data.botData.bot.bot_name}</h6>
                {/* <span className="text-sm font-normal italic text-neutral-600">{localStorage.getItem('email')}</span> */}
            </div>
            
            
        </div>
        <div className='mr-4'>

              <EllipsisVertical />

        </div>
      </div>

        {/* Chat Window */}
        <div className="flex-grow p-4 overflow-y-scroll space-y-4   overflow-y-scroll scrollbar-thin custom-scrollbar ">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.sender != username ? "justify-start" : "justify-end"
              }`}
            >
              <div
                className={`max-w-xs p-3 rounded-lg ${
                  msg.sender === data.botData.bot_name
                    ? "bg-blue-100 text-blue-800"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {msg.message}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Message Input Box */}
        <div className="flex items-center p-4 border-t  border-neutral-800 ">
          <input
            type="text"
            className="flex-grow p-1 rounded-lg border border-gray-300 focus:outline-none"
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyPress}
            placeholder="Type a message..."
          />
          <button
            className="ml-4 p-2 bg-gradient-to-r from-orange-500 to-orange-800 text-white rounded-lg"
            onClick={handleSendMessage}
          >
            <SendHorizontal />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat
