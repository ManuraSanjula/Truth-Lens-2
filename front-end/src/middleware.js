import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher(['/account-preferences(.*)','/dashboard(.*)','/cross-platform-identification(.*)','/report-content(.*)']);

export default clerkMiddleware(async (auth, req) => {
    const { userId, redirectToSignIn } = await auth();

    if (!userId && isProtectedRoute(req)) {
        const url = req.nextUrl.clone();
        url.pathname = '/sign-in'; // Target the sign-in page
        url.searchParams.set('redirectTo', req.nextUrl.pathname);

        return redirectToSignIn({
            redirectUrl: url.toString(),
        });
    }
});

export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // Always run for API routes
        '/(api|trpc)(.*)',
    ],
};