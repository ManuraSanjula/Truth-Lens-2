import {Navigation} from "@/components/Navigation";
import React from "react";
import {IoDocumentTextOutline, IoOpenOutline} from "react-icons/io5";
import {FooterComponent} from "@/components/Footer";
import {BiError} from "react-icons/bi";
import {IoMdCheckmarkCircleOutline} from "react-icons/io";

export default function Page(){
    return (
        <>
            <Navigation/>
            <div className={'mt-10'}>
                <h1 className={'text-3xl font-semibold text-center'}>News verification tool to analyze content authenticity</h1>
                <div id={'verify-content'} className={'mt-10'}>
                    <h2 className={'text-xl text-black font-semibold mx-5 md:mx-10'}>Verify Content</h2>
                    <div className={'p-4 border border-zinc-300 bg-white rounded-md mx-5 md:mx-10 mt-4 space-y-4'}>
                        <h3 className={'text-base flex gap-1'}><IoDocumentTextOutline className={'text-[#4f46e5] text-xl'} />Input Content for Verification</h3>
                        <p className={'text-sm text-gray-400'}>Paste a news article, headline or upload a media to verify its authenticity</p>
                        <form>
                            <label htmlFor={'content'} className={'text-sm text-gray-900 font-semibold'}>Content Type</label>
                            <textarea
                                name={'content'}
                                id={'content'}
                                required
                                className={'w-full h-32 p-3 border border-zinc-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4f46e5]'}
                                placeholder={'Paste news article, headline or URL here...'}
                            />
                            <div className={'flex mt-4'}>
                                <button
                                    type={'submit'}
                                    className={'bg-[#4f46e5] text-[12px] cursor-pointer font-semibold text-white px-4 py-2 rounded-md hover:bg-[#3d36b2] transition duration-200'}
                                >
                                    Analyze Content
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                <div id={'verify-results'} className={'mt-10'}>
                    <h2 className={'text-xl text-black font-semibold mx-5 md:mx-10'}>Verification Results</h2>
                    <div className={'border border-zinc-300 bg-white rounded-md space-y-2 p-4 mt-4 mx-5 md:mx-10'}>
                        <h3 className={'text-gray-400 text-[13px] flex place-items-center gap-2 font-semibold'}>
                            <BiError className={'text-red-600 bg-red-200 rounded-full w-8 h-8 p-2'} />Analysis Result</h3>
                        <h1 className={'text-lg text-red-600 font-semibold'}>Likely False Information</h1>
                        <p className={'text-sm text-gray-400'}>Our AI has determined this content contains misleading or false information with 85% confidence.</p>
                        <div className={'flex gap-2 mt-4'}>
                            <button
                                className={'bg-[#4f46e5] text-[12px] cursor-pointer font-semibold text-white px-4 py-2 rounded-md hover:bg-[#3d36b2] transition duration-200'}
                            >
                                View Detailed Report
                            </button>

                            <button
                                className={'bg-white text-[12px] cursor-pointer text-black border border-zinc-300 px-4 py-2 rounded-md hover:bg-[#f9fafb] transition duration-200'}
                            >
                                Share Report
                            </button>
                        </div>
                    </div>
                </div>
                <div id={'verify-sources'} className={'mt-10'}>
                    <h2 className={'text-xl text-black font-semibold mx-5 md:mx-10'}>Verification Sources</h2>
                    <div className={'space-y-3 mt-4'}>
                        <div className="border border-zinc-300 rounded-md bg-white p-4 mx-5 md:mx-10 flex justify-between items-start">
                            <div>
                                <h3 className="text-[16px] text-black flex items-center gap-1">
                                    <IoMdCheckmarkCircleOutline className="text-xl text-[#4f46e5]" />
                                    <span>Associated Press</span>
                                </h3>
                                <p className="text-zinc-400 text-[13px] mt-1 ml-6">
                                    Contradicting information found in fact check article
                                </p>
                            </div>

                            <IoOpenOutline className="text-zinc-400 text-xl mt-1 cursor-pointer" />
                        </div>
                        <div className="border border-zinc-300 rounded-md bg-white p-4 mx-5 md:mx-10 flex justify-between items-start">
                            <div>
                                <h3 className="text-[16px] text-black flex items-center gap-1">
                                    <IoMdCheckmarkCircleOutline className="text-xl text-[#4f46e5]" />
                                    <span>Associated Press</span>
                                </h3>
                                <p className="text-zinc-400 text-[13px] mt-1 ml-6">
                                    Contradicting information found in fact check article
                                </p>
                            </div>

                            <IoOpenOutline className="text-zinc-400 text-xl mt-1 cursor-pointer" />
                        </div>
                        <div className="border border-zinc-300 rounded-md bg-white p-4 mx-5 md:mx-10 flex justify-between items-start">
                            <div>
                                <h3 className="text-[16px] text-black flex items-center gap-1">
                                    <IoMdCheckmarkCircleOutline className="text-xl text-[#4f46e5]" />
                                    <span>Associated Press</span>
                                </h3>
                                <p className="text-zinc-400 text-[13px] mt-1 ml-6">
                                    Contradicting information found in fact check article
                                </p>
                            </div>

                            <IoOpenOutline className="text-zinc-400 text-xl mt-1 cursor-pointer" />
                        </div>
                    </div>
                </div>

                <div id={'ai-explanation'} className={'mt-10'}>
                    <h2 className={'text-xl text-black font-semibold mx-5 md:mx-10'}>AI Explanation</h2>
                    <div className="border border-zinc-200 bg-white rounded-md p-5 mx-5 mt-4 md:mx-10 space-y-4">
                        <div className="space-y-2">
                            <h3 className="text-[15px] font-semibold text-black">
                                Why We Flagged This Content
                            </h3>
                            <p className="text-sm text-zinc-500 leading-relaxed text-justify">
                                This content contains several red flags typical of misinformation: unverified sources, contradictory data compared to official records, manipulated context, and emotional language designed to provoke outrage rather than inform. Multiple fact-checking organizations have previously debunked similar claims.
                            </p>
                        </div>

                        <div className="flex gap-3 pt-2">
                            <button className="text-sm text-indigo-600 cursor-pointer border border-indigo-600 rounded-md px-4 py-2 hover:bg-indigo-50 transition">
                                Share Result
                            </button>
                            <button className="text-sm text-red-600 cursor-pointer border border-red-600 rounded-md px-4 py-2 hover:bg-red-50 transition">
                                Report Inaccuracy
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <FooterComponent/>
        </>
    )
}