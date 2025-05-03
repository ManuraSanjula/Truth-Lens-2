'use client';
import React, {useState} from "react";
import { Button, Navbar, NavbarBrand, NavbarCollapse, NavbarToggle } from "flowbite-react";
import { MenuItem, ProductItem } from "@/components/ui/navbar-menu";
import Link from "next/link";
import {SignedIn, SignedOut, UserButton} from "@clerk/nextjs";
import {LuSettings2} from "react-icons/lu";

export function Navigation() {
    const [active, setActive] = useState(null);

    return (
        <div>
            <Navbar fluid
                    onMouseLeave={() => setActive(null)}
                    style={{backgroundColor: "white"}}>
                <NavbarBrand href="/">
                    <span className="self-center whitespace-nowrap text-xl font-semibold text-[#4f46e5]">TruthLens</span>
                </NavbarBrand>
                <div className="flex place-items-center md:order-2 gap-3">
                    <SignedOut>
                        <Link href={'/sign-in'} className={'hidden md:block text-[#4f46e5] font-semibold text-sm'}>Login</Link>
                        <Button as={Link} href={'/sign-up'} className={'hidden md:block cursor-pointer p-2'} style={{backgroundColor: '#4f46e5'}}>Sign Up</Button>
                    </SignedOut>
                    <SignedIn>
                        <UserButton>
                            <UserButton.MenuItems>
                                <UserButton.Link
                                    label="Preferences"
                                    labelIcon={<LuSettings2 className={'font-bold'} />}
                                    href="/account-preferences"
                                />
                            </UserButton.MenuItems>
                        </UserButton>
                    </SignedIn>
                    <NavbarToggle />
                </div>
                <NavbarCollapse>
                    <MenuItem setActive={setActive} active={active} textPresence={false} item="Home" href={'/'}>
                    </MenuItem>
                    <MenuItem setActive={setActive} active={active} textPresence={false} item="About" href={'/about'}></MenuItem>
                    <MenuItem setActive={setActive} active={active} textPresence={false} item="Dashboard" href={'/stats'}></MenuItem>
                    <MenuItem setActive={setActive} active={active} textPresence={true} item="Tools" href={'#'}>
                        <div className="  text-sm grid grid-cols-1 md:grid-cols-2 gap-10 p-4">
                            <ProductItem
                                title="Verify News"
                                href="/verify-news"
                                src="https://assets.aceternity.com/demos/algochurn.webp"
                                description="Quickly fact-check news articles and social media posts using AI-powered tools." />
                            <ProductItem
                                title="Deepfake Detection"
                                href="/deepfake-detection"
                                src="https://assets.aceternity.com/demos/tailwindmasterkit.webp"
                                description="Identify altered or synthetic media to combat misinformation and fake content." />
                            <ProductItem
                                title="Cross-Platform"
                                href="/cross-platform-identification"
                                src="https://assets.aceternity.com/demos/Screenshot+2024-02-21+at+11.51.31%E2%80%AFPM.png"
                                description="Detect and trace misinformation across various platforms in real time." />
                            <ProductItem
                                title="Report Misinformation"
                                href="/report-content"
                                src="https://assets.aceternity.com/demos/Screenshot+2024-02-21+at+11.47.07%E2%80%AFPM.png"
                                description="Easily report false or misleading content to help build a safer internet." />
                        </div>
                    </MenuItem>
                    <MenuItem setActive={setActive} active={active} textPresence={false} item="Monitor" href={'/monitor'}></MenuItem>
                    <SignedOut>
                        <Link href={'/sign-in'} className={'block md:hidden text-[#4f46e5] font-semibold text-sm text-center my-2'}>Login</Link>
                        <Button as={Link} href={'/sign-up'} className={'block md:hidden cursor-pointer p-2'} style={{backgroundColor: '#4f46e5'}}>Sign Up</Button>
                    </SignedOut>
                </NavbarCollapse>
            </Navbar>
        </div>
    );
}
