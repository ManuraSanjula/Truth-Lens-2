import {Navigation} from "@/components/Navigation";
import BarChart from "@/components/BarChart";
import {Table, TableBody, TableCell, TableHead, TableHeadCell, TableRow} from "flowbite-react";
import {FooterComponent} from "@/components/Footer";

export default function Page(){
    return(
        <>
            <Navigation/>
            <h1 className={'text-2xl font-semibold mx-5 md:mx-10 mt-10'}>Dashboard Overview</h1>
            <div className={'h-screen'}>
                <div className={'mt-10 grid grid-cols-1 md:grid-cols-3 gap-3 mx-5 md:mx-10'}>
                    <div className="bg-white rounded-md border border-zinc-300 p-4 flex justify-between">
                        <div>
                            <h2 className="text-base text-zinc-400 mb-2">Total Scans</h2>
                            <p className="text-2xl font-bold">1,234</p>
                        </div>
                        <p className={'text-lime-600'}>12%</p>
                    </div>
                    <div className="bg-white rounded-md border border-zinc-300 p-4 flex justify-between">
                        <div>
                            <h2 className="text-base text-zinc-400 mb-2">Detected Fake</h2>
                            <p className="text-2xl font-bold">456</p>
                        </div>
                        <p className={'text-red-600'}>-5%</p>
                    </div>
                    <div className="bg-white rounded-md border border-zinc-300 p-4 flex justify-between">
                        <div>
                            <h2 className="text-base text-zinc-400 mb-2">Accuracy Rate</h2>
                            <p className="text-2xl font-bold">94%</p>
                        </div>
                        <p className={'text-lime-600'}>+2%</p>
                    </div>
                </div>
                <div className={'mt-10 grid grid-cols-1 md:grid-cols-2 gap-3 mx-5 md:mx-10'}>
                    <div className={'bg-white rounded-md border border-zinc-300 p-4'}>
                        <h4 className={'font-semibold text-sm'}>Misinformation Trends</h4>
                        <BarChart/>
                    </div>
                    <div className={'bg-white rounded-md border border-zinc-300 p-4'}>
                        <h4 className={'font-semibold text-sm'}>Recent Reports</h4>
                        <div className="overflow-x-auto mt-4">
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableHeadCell>Title</TableHeadCell>
                                        <TableHeadCell>Source</TableHeadCell>
                                        <TableHeadCell>Confidence</TableHeadCell>
                                        <TableHeadCell>Date</TableHeadCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody className="divide-y">
                                    <TableRow className="bg-white border-gray-700">
                                        <TableCell className="whitespace-nowrap font-medium text-gray-900">
                                            Election Misinformation
                                        </TableCell>
                                        <TableCell>Twitter</TableCell>
                                        <TableCell>95%</TableCell>
                                        <TableCell>May 15, 2023</TableCell>
                                    </TableRow>
                                    <TableRow className="bg-white border-gray-700">
                                        <TableCell className="whitespace-nowrap font-medium text-gray-900">
                                            Election Misinformation
                                        </TableCell>
                                        <TableCell>Twitter</TableCell>
                                        <TableCell>95%</TableCell>
                                        <TableCell>May 15, 2023</TableCell>
                                    </TableRow>
                                    <TableRow className="bg-white border-gray-700">
                                        <TableCell className="whitespace-nowrap font-medium text-gray-900">
                                            Election Misinformation
                                        </TableCell>
                                        <TableCell>Twitter</TableCell>
                                        <TableCell>95%</TableCell>
                                        <TableCell>May 15, 2023</TableCell>
                                    </TableRow>
                                </TableBody>
                            </Table>
                        </div>
                    </div>
                </div>
            </div>
            <FooterComponent/>
        </>
    )
}