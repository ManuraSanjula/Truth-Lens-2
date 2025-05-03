import {Navigation} from "@/components/Navigation";
import React from "react";
import {FileInput, HR, Label, List, ListItem} from "flowbite-react";
import {BiError} from "react-icons/bi";
import {FooterComponent} from "@/components/Footer";


export default function Page(){
    return(
        <>
            <Navigation/>
            <div className={'my-10'}>
                <h1 className={'text-3xl font-semibold text-center'}>Deepfake Detection</h1>
                <p className={'text-gray-400 text-center text-base'}>Upload an image or video to analyze for potential AI-generated or manipulated media</p>
                <div className={'p-4 border border-zinc-300 bg-white rounded-md mx-5 md:mx-10 mt-10 space-y-4'}>
                    <h2 className={'text-xl text-black font-semibold'}>Upload Media</h2>
                    <form>
                        <div className="flex w-full items-center justify-center">
                            <Label
                                htmlFor="dropzone-file"
                                className="flex h-64 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed
                                border-gray-300 bg-gray-50 hover:bg-gray-100 dark:border-gray-600
                                dark:hover:border-gray-500"
                            >
                                <div className="flex flex-col items-center justify-center pb-6 pt-5">
                                    <svg
                                        className="mb-4 h-8 w-8 text-gray-500 dark:text-gray-400"
                                        aria-hidden="true"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 20 16"
                                    >
                                        <path
                                            stroke="currentColor"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="2"
                                            d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                                        />
                                    </svg>
                                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                                        <span className="font-semibold">Click to upload</span> or drag and drop
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG or GIF (MAX. 800x400px)</p>
                                </div>
                                <FileInput id="dropzone-file" className="hidden" />
                            </Label>
                        </div>
                        <button
                            type={'submit'}
                            className={'bg-[#4f46e5] mt-4 text-sm cursor-pointer font-semibold text-white px-4 py-2 rounded-md hover:bg-[#3d36b2] transition duration-200'}
                        >
                            Analyze Media
                        </button>
                    </form>
                    <hr className={'text-zinc-300 mx-20 my-10 rounded-4xl'}/>
                    <h3 className={'text-lg text-black font-semibold'}>Analysis Result</h3>
                    <div className={'bg-[#fef2f2] rounded-md p-4 space-y-3'}>
                        <h3 className={'text-red-600 text-base flex gap-1 place-items-center font-semibold'}>
                            <BiError className={'text-red-600 text-xl'} />
                            87% Likely Manipulated</h3>
                        <p className={'text-sm text-red-600'}>Our analysis detected significant indicators of AI
                            manipulation in this media.</p>
                    </div>
                    <div className={'grid grid-cols-1 md:grid-cols-2 gap-3'}>
                        <div className={'bg-[#f9fafb] p-4'}>
                            <h4 className={'text-sm font-semibold'}>Manipulation Strategy</h4>
                            <ul className={'text-sm text-zinc-700 mt-4'}>
                                <li className={'flex justify-between'}>
                                    <span>Face Swapping</span>
                                    <span>95%</span>
                                </li>
                                <li className={'flex justify-between'}>
                                    <span>Face Swapping</span>
                                    <span>95%</span>
                                </li>
                                <li className={'flex justify-between'}>
                                    <span>Face Swapping</span>
                                    <span>95%</span>
                                </li>
                                <li className={'flex justify-between'}>
                                    <span>Face Swapping</span>
                                    <span>95%</span>
                                </li>
                            </ul>
                        </div>

                        <div className={'bg-[#f9fafb] p-4'}>
                            <h4 className={'text-sm font-semibold'}>Detection Method</h4>
                            <ul className={'text-sm text-zinc-700 mt-4 list-disc ml-4'}>
                                <li>Neural Network Analysis</li>
                                <li>Neural Network Analysis</li>
                                <li>Neural Network Analysis</li>
                                <li>Neural Network Analysis</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <FooterComponent/>
        </>
    )
}