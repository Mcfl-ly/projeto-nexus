import { useContext } from "react";
import { LibraryContext } from "./libraryContext.js";
export default function useLibrary() {
    const library = useContext(LibraryContext);
    if (!library) throw new Error("A biblioteca precisa de LibraryProvider.");
    return library;
}
