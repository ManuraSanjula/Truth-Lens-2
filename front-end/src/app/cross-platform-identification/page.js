import {Navigation} from "@/components/Navigation";
import React from "react";
import {IoSearch} from "react-icons/io5";
import {FiGlobe} from "react-icons/fi";
import {IoMdCheckmarkCircleOutline} from "react-icons/io";
import {Progress} from "flowbite-react";
import {FooterComponent} from "@/components/Footer";

export default function Page(){
    return(
        <>
            <Navigation/>
            <div className={'my-10 h-screen'}>
                <h1 className={'text-3xl font-semibold text-center'}>Cross-platform Fact-checking</h1>
                <p className={'text-center text-zinc-400'}>Platform for verifying claims with both AI and Human review</p>

                <div className={'grid grid-cols-1 md:grid-cols-2 mt-4'}>
                    <div className={'p-4 border border-zinc-300 bg-white rounded-md mx-5 md:mx-10 mt-4 space-y-4'}>
                        <h3 className={'text-base font-semibold'}>Quick Cross Review</h3>
                        <form className={'space-y-5'}>
                            <label className={'text-sm'}>Platform URL</label>
                            <div className={'flex items-center gap-2'}>
                                <input
                                    type="text"
                                    id={'platform_url'}
                                    required
                                    name={'platform_url'}
                                    className={'w-full p-2 border border-zinc-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4f46e5]'}
                                    placeholder={'Paste platform URL here...'}
                                />
                                <button
                                    className={'bg-[#4f46e5] text-[12px] cursor-pointer font-semibold text-white px-4 py-2 rounded-md hover:bg-[#3d36b2] transition duration-200'}
                                >
                                    <IoSearch className={'text-2xl font-semibold place-items-center'} />
                                </button>
                            </div>

                            <div id={'conditional_div'} className={'hidden'}></div>

                            <label htmlFor={'content_type'} className={'text-sm'}>Content Type</label>
                            <select
                                name={'content_type'}
                                id={'content_type'}
                                required
                                defaultValue={'Select Content Type'}
                                className={'w-full p-2 border border-zinc-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4f46e5]'}
                            >
                                <option value="news_article">News Article</option>
                                <option value="social_media_post">Social Media Post</option>
                                <option value="video">Video</option>
                                <option value="image">Image</option>
                                <option value="other">Other</option>
                            </select>

                            <div className={'flex items-center justify-center'}>
                                <button
                                    type={'submit'}
                                    className={'bg-[#4f46e5] text-sm cursor-pointer text-white ' +
                                        'px-4 py-2 rounded-md hover:bg-[#3d36b2] transition duration-200 w-full'}
                                >
                                    Start Verification
                                </button>
                            </div>
                        </form>
                    </div>
                    <div className={'p-4 border border-zinc-300 bg-white rounded-md mx-5 md:mx-10 mt-4 space-y-5'}>
                        <h3 className={'text-base font-semibold'}>Verification Status</h3>
                        <div className={'flex flex-row gap-2 place-items-center bg-[#f9fafb] p-2 rounded-md'}>
                            <FiGlobe className={'text-[#4f46e5] text-sm rounded-full w-8 h-8 p-2 bg-[#e0e7ff]'} />
                            <div>
                                <h4 className={'text-sm font-semibold'}>AI Analysis</h4>
                                <p className={'text-[12px] text-zinc-400'}>Automated verification in progress...</p>
                            </div>
                        </div>
                        <div className={'flex flex-row gap-2 place-items-center bg-[#f9fafb] p-2 rounded-md'}>
                            <IoMdCheckmarkCircleOutline className="text-[#16a34a] text-sm rounded-full w-8 h-8 p-2 bg-[#dcfce7]" />
                            <div>
                                <h4 className={'text-sm font-semibold'}>Human Verification</h4>
                                <p className={'text-[12px] text-zinc-400'}>Expert fact-checkers' review</p>
                            </div>
                        </div>

                        <div>
                            <Progress
                                size="md"
                                progress={52}
                            />
                            <div className="text-[12px] font-medium text-zinc-400 mt-1">Verification Progress: 52%</div>
                        </div>
                    </div>
                </div>
            </div>
            <FooterComponent/>
        </>
    )
}