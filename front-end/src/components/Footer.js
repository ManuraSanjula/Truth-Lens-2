import { Footer, FooterCopyright, FooterLink, FooterLinkGroup } from "flowbite-react";

export function FooterComponent() {
    return (
        <Footer container
                style={{backgroundColor: "white"}}
                className="rounded-none mt-10">
            <FooterCopyright href="#" by="TruthLens™" year={2025} />
            <FooterLinkGroup>
                <FooterLink href="#" className={'text-zinc-400'}>About</FooterLink>
                <FooterLink href="#" className={'text-zinc-400'}>Privacy Policy</FooterLink>
                <FooterLink href="#" className={'text-zinc-400'}>Licensing</FooterLink>
                <FooterLink href="#" className={'text-zinc-400'}>Contact</FooterLink>
            </FooterLinkGroup>
        </Footer>
    );
}
