'use client'
import {Navigation} from "@/components/Navigation";
import { ToggleSwitch } from "flowbite-react";
import { useState } from "react";
import {IoIosArrowForward} from "react-icons/io";
import BarChart from "@/components/BarChart";

export default function Page(){
    const [switchEmail, setSwitchEmail] = useState(false);
    const [push, setPush] = useState(false);
    const [digest, setDigest] = useState(false);
    return(
        <>
            <Navigation/>
            <h1 className={'text-2xl font-semibold my-10 mx-5 md:mx-10'}>Settings</h1>
            <div className={'mx-5 md:mx-10'}>
                <form className={'space-y-4'}>
                    <div>
                        <h2 className={'font-semibold text-lg'}>Notification Preferences</h2>
                        <div className={'grid grid-cols-1 mt-4 space-y-4'}>
                            <div className={'flex justify-between bg-white border border-zinc-300 rounded-md p-4 place-items-center'}>
                                <div>
                                    <h4 className={'font-semibold'}>Email Notifications</h4>
                                    <p className={'text-zinc-400 text-sm'}>Receive important updates via email</p>
                                </div>
                                <ToggleSwitch checked={switchEmail} onChange={setSwitchEmail}/>
                            </div>
                            <div className={'flex justify-between bg-white border border-zinc-300 rounded-md p-4 place-items-center'}>
                                <div>
                                    <h4 className={'font-semibold'}>Push Notifications</h4>
                                    <p className={'text-zinc-400 text-sm'}>Get alerts on your device</p>
                                </div>
                                <ToggleSwitch checked={push} onChange={setPush}/>
                            </div>
                            <div className={'flex justify-between bg-white border border-zinc-300 rounded-md p-4 place-items-center'}>
                                <div>
                                    <h4 className={'font-semibold'}>Weekly Digest</h4>
                                    <p className={'text-zinc-400 text-sm'}>Summary of verified news each week</p>
                                </div>
                                <ToggleSwitch checked={digest} onChange={setDigest}/>
                            </div>
                        </div>
                    </div>
                    <div>
                        <h2 className={'font-semibold text-lg'}>Content Preferences</h2>
                        <div className={'grid grid-cols-1 mt-4 space-y-4'}>
                            <div className={'flex justify-between bg-white border border-zinc-300 rounded-md p-4 place-items-center'}>
                                <div>
                                    <h4 className={'font-semibold'}>Topics of Interest</h4>
                                    <p className={'text-zinc-400 text-sm'}>Customize your news categories</p>
                                </div>
                                <button><IoIosArrowForward className={'text-zinc-400 text-lg cursor-pointer'} /></button>
                            </div>
                            <div className={'flex justify-between bg-white border border-zinc-300 rounded-md p-4 place-items-center'}>
                                <div>
                                    <h4 className={'font-semibold'}>Language</h4>
                                    <p className={'text-zinc-400 text-sm'}>Select preferred language</p>
                                </div>
                                <select
                                    className={'text-sm'}
                                    defaultValue={'English'}
                                >
                                    <option value="English">English</option>
                                    <option value="Spanish">Spanish</option>
                                    <option value="French">French</option>
                                    <option value="German">German</option>
                                </select>
                            </div>
                            <div className={'flex justify-between bg-white border border-zinc-300 rounded-md p-4 place-items-center'}>
                                <div>
                                    <h4 className={'font-semibold'}>Region</h4>
                                    <p className={'text-zinc-400 text-sm'}>Set your geographic focus</p>
                                </div>
                                <select
                                    className={'text-sm'}
                                    defaultValue={'Local'}
                                >
                                    <option value="Global">Global</option>
                                    <option value="Local">Local</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <button
                        className={'bg-[#4f46e5] text-white font-semibold text-sm rounded-md p-2 mt-6'}
                        type={'submit'}
                    >
                        Save Changes
                    </button>
                </form>
            </div>
        </>
    )
}