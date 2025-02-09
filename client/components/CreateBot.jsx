import { useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const CreateBot = () => {
  const [formData, setFormData] = useState({
    email: localStorage.getItem('email'),
    bot_name: "",
    description: "",
    start_message: "",
    image_file: null,
    pdf_files: [],
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files) {
      if (e.target.name === "image_file" && files[0].type.startsWith("image/")) {
        setFormData({ ...formData, image_file: files[0] });
      } else if (e.target.name === "pdf_files") {
        const pdfFiles = Array.from(files).filter(file => file.type === "application/pdf");
        setFormData({ ...formData, pdf_files: pdfFiles });
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formDataToSend = new FormData();
    Object.keys(formData).forEach((key) => {
        if (key === "pdf_files") {
            formData[key].forEach(file => {
              formDataToSend.append("pdf_files", file);
            });
      } else if (formData[key]) {
        formDataToSend.append(key, formData[key]);
      }
    });

    try {
      const response = await axios.post("https://chat-persona-ai-ov46.vercel.app/add_user_bot/", formDataToSend, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log("Response:", response.data);
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  return (
    <div className="flex flex-col items-center ">
      <div className="p-10 border border-neutral-700 rounded-xl w-[500px]">
        <h2 className="text-3xl sm:text-3xl lg:text-4xl text-center tracking-wide bg-gradient-to-r from-orange-500 to-red-800 text-transparent bg-clip-text">
          Create Your Own Bot
        </h2>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">

          <input
            type="text"
            name="bot_name"
            placeholder="Bot Name"
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
          <textarea
            name="description"
            placeholder="Description"
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          ></textarea>

          <input
            type="text"
            name="start_message"
            placeholder="Start Message"
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
          <label className="block text-white">Upload an Image:</label>
          <input
            type="file"
            name="image_file"
            onChange={handleFileChange}
            accept="image/*"
            className="w-full px-4 py-2 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
          
          <label className="block text-white">Upload a PDF:</label>
          <input
            type="file"
            name="pdf_files"
            onChange={handleFileChange}
            accept="application/pdf"
            multiple
            className="w-full px-4 py-2 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />

          <button
            type="submit"
            className="inline-flex justify-center items-center text-center w-full h-12 px-6 text-lg font-medium text-white bg-orange-700 hover:bg-orange-800 border border-orange-700 rounded-lg transition duration-200"
          >
            Create
          </button>
        </form>
      </div>

     
    </div>
  );
};

export default CreateBot;
