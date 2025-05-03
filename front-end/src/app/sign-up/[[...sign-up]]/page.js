import { SignUp } from '@clerk/nextjs'
import {FooterComponent} from "@/components/Footer";

export default function Page() {
    return(
        <>
            <div className={'flex items-center justify-center h-screen'}>
                <SignUp />
            </div>
            <FooterComponent/>
        </>
    )
}