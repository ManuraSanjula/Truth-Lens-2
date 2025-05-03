'use client'
import React from "react";
import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";
import {Button} from "flowbite-react";
import {TbVaccine} from "react-icons/tb";
import {MdOutlineHowToVote} from "react-icons/md";
import {FiBarChart, FiCloud} from "react-icons/fi";
import {IoDocumentTextOutline} from "react-icons/io5";
import {LuBrain} from "react-icons/lu";

export default function HeroSection(){
    const placeholders = [
        "Aliens Demand Wi-Fi Password After Parking UFO in Times Square",
        " Cat Becomes Mayor of Small Town, Immediately Bans All Dogs",
        "Government Accidentally Sends Stimulus Check to Elon Musk",
        "https://x.com/WhiteHouse/status/1910878920108302438",
        "Chicken Crosses Road, Refuses to Explain Motives to Reporters",
    ];

    const handleChange = (e) => {
        console.log(e.target.value);
    };

    const onSubmit = async (e) => {
        e.preventDefault();

        const formdata = new FormData();
        // Get the input value from the form
        const inputValue = e.target.querySelector('input').value;
        
        // Add required parameters to form data
        formdata.append('content_type', 'url');
        formdata.append('source_url', inputValue);
        formdata.append('user_id', '6804a44d00830494ddddbafd');
        
        const response = await fetch('http://localhost:8000/api/v1/content/submit', {
            method: 'POST',
            body: formdata,
        });
        
        if(!response.ok){
            console.log('Error submitting content');
        } else {
            const data = await response.json();
            console.log(data);
        }
    };
    
    return(
        <>
            <div className={'my-10'}>
                <h1 className={'text-4xl text-center font-semibold'}>Verify News & Combat Misinformation</h1>
                <p className={'text-lg text-center font-normal mt-2'}>Our AI-powered platform helps you identify
                    fake news and verify information accuracy</p>
                <div className={'mt-20 mx-5'}>
                    <PlaceholdersAndVanishInput
                        placeholders={placeholders}
                        onChange={handleChange}
                        onSubmit={onSubmit}
                    />
                    <p className={'text-sm text-gray-500 text-center mt-1 opacity-45'}>(Paste news headline or URL to verify)</p>
                </div>
            </div>
            {/*body starts here*/}
            <div>
                <h2 className={'text-xl text-black font-semibold mx-5 md:mx-10'}>Trending Misinformation</h2>
                <div className={'grid grid-cols-1 md:grid-cols-3 gap-y-4 gap-4 mx-5 md:mx-10 mt-5'}>
                    <div className={'bg-[#fef2f2] p-8 space-y-3 rounded-md min-w-full md:max-w-full'}>
                        <TbVaccine className={'text-red-500 text-xl'} />
                        <h3 className={'text-black font-semibold'}>COVID-19 Vaccine Claim</h3>
                        <p className={'text-gray-600'}>Viral social media post claims vaccines contain microchips - Fact check reveals this is false</p>
                        <button className={'text-[#4f46e5] bg-white px-4 py-2 rounded-md border border-zinc-300'}>View Analysis</button>
                    </div>
                    <div className={'bg-[#eff6ff] p-8 space-y-3 rounded-md min-w-full md:max-w-full'}>
                        <MdOutlineHowToVote className={'text-blue-600 text-xl'} />
                        <h3 className={'text-black font-semibold'}>COVID-19 Vaccine Claim</h3>
                        <p className={'text-gray-600'}>Viral social media post claims vaccines contain microchips - Fact check reveals this is false</p>
                        <button className={'text-[#4f46e5] bg-white px-4 py-2 rounded-md border border-zinc-300'}>View Analysis</button>
                    </div>
                    <div className={'bg-[#f0fdf4] p-8 space-y-3 rounded-md min-w-full md:max-w-full'}>
                        <FiCloud className={'text-green-500 text-xl'} />
                        <h3 className={'text-black font-semibold'}>COVID-19 Vaccine Claim</h3>
                        <p className={'text-gray-600'}>Viral social media post claims vaccines contain microchips - Fact check reveals this is false</p>
                        <button className={'text-[#4f46e5] bg-white px-4 py-2 rounded-md border border-zinc-300'}>View Analysis</button>
                    </div>
                </div>
            </div>

            <div>
                <h2 className={'text-xl text-black font-semibold mt-10 mx-5 md:mx-10'}>How It Works</h2>
                <div className={'grid grid-cols-1 md:grid-cols-3 gap-y-4 gap-4 mx-5 md:mx-10 mt-5'}>
                    <div className={'p-8 space-y-3 border border-zinc-300 rounded-md min-w-full md:max-w-full'}>
                        <IoDocumentTextOutline className={'p-2 bg-white rounded-md border border-zinc-300 text-[#4f46e5] text-xl w-10 h-10'} />
                        <h3 className={'text-black font-normal'}>Step 1</h3>
                        <h2 className={'text-black font-semibold'}>Submit Content</h2>
                        <p className={'text-gray-600 text-sm'}>Viral social media post claims vaccines contain microchips - Fact check reveals this is false</p>
                    </div>
                    <div className={'p-8 space-y-3 border border-zinc-300 rounded-md min-w-full md:max-w-full'}>
                        <LuBrain className={'p-2 bg-white rounded-md border border-zinc-300 text-[#4f46e5] text-xl w-10 h-10'} />
                        <h3 className={'text-black font-normal'}>Step 2</h3>
                        <h2 className={'text-black font-semibold'}>AI Analysis</h2>
                        <p className={'text-gray-600 text-sm'}>Viral social media post claims vaccines contain microchips - Fact check reveals this is false</p>
                    </div>
                    <div className={'p-8 space-y-3 border border-zinc-300 rounded-md min-w-full md:max-w-full'}>
                        <FiBarChart className={'p-2 bg-white rounded-md border border-zinc-300 text-[#4f46e5] text-xl w-10 h-10'} />
                        <h3 className={'text-black font-normal'}>Step 3</h3>
                        <h2 className={'text-black font-semibold'}>Get Results</h2>
                        <p className={'text-gray-600 text-sm'}>Viral social media post claims vaccines contain microchips - Fact check reveals this is false</p>
                    </div>
                </div>
            </div>
        </>
    )
}