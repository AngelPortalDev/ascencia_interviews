import { createContext, useContext,useState} from "react";

const PermissionContext = createContext();

export const usePermission = () => useContext(PermissionContext);

export const PermissionProvider = ({children}) =>{





    const [termsAccept, setTermsAccept] = useState(
        localStorage.getItem("termsAccepted") === "true"
    )

    const [audioVideoAccepted, setAudioVideoAccepted] = useState(
        localStorage.getItem("hasPermissions") === "true"
    )


    const acceptTerms = ()=>{
        setTermsAccept(true);
        localStorage.setItem("termsAccepted", "true");
    }

    const acceptAudioVideo = ()=>{
        setAudioVideoAccepted(true);
        localStorage.setItem("hasPermissions", "true");
    }



    console.log("Context Values:", { termsAccept, audioVideoAccepted });

    return(
       <PermissionContext.Provider value={{termsAccept,audioVideoAccepted,acceptAudioVideo, acceptTerms}}>
        {children}
       </PermissionContext.Provider>   
    )
}