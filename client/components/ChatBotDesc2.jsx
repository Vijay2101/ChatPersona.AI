import React from 'react'

const ChatBotDesc2 = ({ data }) => {
  return (
    <div className=''>
        {/* <h1 className=" text-2xl sm:text-1xl lg:text-1xl  tracking-wide  bg-clip-text text-center">
                Description
        </h1> */}
        <p className='mt-5 lg:mr-10 lg:ml-10 tracking-wide'>
            {data.bot.description}
        </p>
    </div>
  )
}

export default ChatBotDesc2
