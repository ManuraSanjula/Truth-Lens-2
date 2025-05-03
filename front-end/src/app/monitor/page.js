import {Navigation} from "@/components/Navigation";
import {Progress} from "flowbite-react";
import {FooterComponent} from "@/components/Footer";

export default function Page(){
    return(
        <>
            <Navigation/>
            <div className={'h-screen'}>
                <h1 className={'text-2xl font-bold text-center mt-10'}>Real-Time Misinformation Monitor</h1>
                <p className={'text-center text-sm text-zinc-400'}>Track and analyze potential misinformation in real-time</p>
                <div className={'grid grid-cols-1 md:grid-cols-2 mx-5 md:mx-10 mt-10 gap-3'}>
                    <div className={'bg-white rounded-md border border-zinc-300 p-4'}>
                        <div className={'flex justify-between place-items-center'}>
                            <h3 className={'font-semibold'}>Live Feed of Fake News Alerts</h3>
                            <div className={'flex flex-row gap-1'}>
                                <div className={'rounded-full bg-red-400 flex items-center justify-center w-4 h-4'}>
                                    <div className={'rounded-full bg-red-700 animate-ping w-1 h-1'}></div>
                                </div><span className={'text-[12px] text-zinc-400'}>Live</span>
                            </div>
                        </div>

                        <div className={'flex justify-between place-items-center mt-4'}>
                            <div>
                                <h3 className={'font-semibold text-sm'}>Potential Vaccine Misinformation</h3>
                                <p className={'text-[12px] text-zinc-500'}>Twitter News Feed</p>
                                <p className={'text-[10px] text-zinc-400'}>10min ago</p>
                            </div>
                            <div className={'flex items-center justify-center rounded-md w-24 h-8 p-2 bg-red-300'}>
                                <p className={'text-sm text-red-900 font-semibold'}>High Risk</p>
                            </div>
                        </div>
                        <hr className={'text-zinc-200 my-4'}/>
                        <div className={'flex justify-between place-items-center mt-4'}>
                            <div>
                                <h3 className={'font-semibold text-sm'}>Election Coverage</h3>
                                <p className={'text-[12px] text-zinc-500'}>News Sites</p>
                                <p className={'text-[10px] text-zinc-400'}>30min ago</p>
                            </div>
                            <div className={'flex items-center justify-center rounded-md w-24 h-8 p-2 bg-green-300'}>
                                <p className={'text-sm text-green-700 font-semibold'}>Low Risk</p>
                            </div>
                        </div>
                        <hr className={'text-zinc-200 my-4'}/>
                        <div className={'flex justify-between place-items-center mt-4'}>
                            <div>
                                <h3 className={'font-semibold text-sm'}>Climate Change Report</h3>
                                <p className={'text-[12px] text-zinc-500'}>Facebook Groups</p>
                                <p className={'text-[10px] text-zinc-400'}>15min ago</p>
                            </div>
                            <div className={'flex items-center justify-center rounded-md w-28 h-8 p-2 bg-yellow-100'}>
                                <p className={'text-sm text-yellow-700 font-semibold'}>Medium Risk</p>
                            </div>
                        </div>
                        <hr className={'text-zinc-200 my-4'}/>
                    </div>
                    <div className={'bg-white rounded-md border border-zinc-300 p-4'}>
                        <h3 className={'font-semibold'}>Trending Topics</h3>
                        <ul className={'mt-4 ml-2 leading-loose'}>
                            <div>
                                <li>HealthCare</li>
                                <Progress size="sm" color={'blue'} progress={50}/>
                            </div>
                            <div>
                                <li>Politics</li>
                                <Progress size="sm" color={'blue'} progress={25}/>
                            </div>
                            <div>
                                <li>Technology</li>
                                <Progress size="sm" color={'blue'} progress={75}/>
                            </div>
                            <div>
                                <li>Environment</li>
                                <Progress size="sm" color={'blue'} progress={60}/>
                            </div>
                        </ul>
                    </div>
                </div>
            </div>
            <FooterComponent/>
        </>
    )
}