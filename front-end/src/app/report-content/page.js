'use client';
import {Navigation} from "@/components/Navigation";
import React,{useState} from "react";
import {FooterComponent} from "@/components/Footer";

const reasons = [
    { label: "Misleading Content", description: "Content that misleads or confuses" },
    { label: "Fake Content", description: "Completely fabricated information" },
    { label: "Manipulated Content", description: "Genuine content that has been altered" },
    { label: "Other", description: "Does not fit any of the above" }
];

export default function Page(){
    const [selected, setSelected] = useState(null);

    return(
        <>
            <Navigation/>
            <div className={'my-10 h-screen'}>
                <h1 className={'text-3xl font-semibold text-center'}>Report Suspicious News</h1>
                <p className={'text-sm text-zinc-400 text-center'}>Help combat misinformation by reporting suspicious content</p>
                <div className={'p-4 border border-zinc-300 bg-white rounded-md mx-5 md:mx-10 mt-10 space-y-4'}>
                    <h2 className={'text-xl text-black font-semibold'}>Quick Submit</h2>
                    <form className={'space-y-3'}>
                        <label htmlFor={'contentUrl_text'} className={'text-[12px] text-gray-900'}>Content URL or Text</label>
                        <textarea
                            name={'contentUrl_text'}
                            id={'contentUrl_text'}
                            required
                            className={'w-full h-32 p-3 border border-zinc-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4f46e5]'}
                            placeholder={'Paste news article, headline or URL here...'}
                        />
                        <label htmlFor={'reason'} className={'text-[12px] text-gray-900'}>Why do you think this is suspicious?</label>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mt-1">
                            {reasons.map((reason, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setSelected(idx)}
                                    id={'reason'}
                                    name={'reason'}
                                    value={reason.label}
                                    className={`rounded-lg border p-4 text-left transition-all ${
                                        selected === idx
                                            ? "border-[#4f46e5] bg-blue-50 shadow-sm"
                                            : "border-gray-300 hover:border-blue-400"
                                    }`}
                                >
                                    <p className="font-semibold text-sm text-gray-800">{reason.label}</p>
                                    <p className="text-sm text-gray-500">{reason.description}</p>
                                </button>
                            ))}
                        </div>
                        <label htmlFor={'additional_content'} className={'text-[12px] text-gray-900'}>Additional Information</label>
                        <textarea
                            name={'additional_content'}
                            id={'additional_content'}
                            required
                            className={'w-full h-32 p-3 border border-zinc-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4f46e5]'}
                            placeholder={'Provide any additional information or context that may help in the review process...'}
                        />

                        <div className={'flex'}>
                            <button
                                type={'submit'}
                                className={'bg-[#4f46e5] text-sm cursor-pointer font-semibold text-white px-4 py-2 rounded-md hover:bg-[#3d36b2] transition duration-200'}
                            >
                                Submit Report
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            <FooterComponent/>
        </>
    )
}