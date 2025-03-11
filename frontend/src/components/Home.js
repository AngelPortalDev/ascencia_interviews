import { NavLink,useParams} from "react-router-dom";
import Interview from '../assest/Interview.png';
import useInterviewLinkStatus  from '../hooks/useInterviewLinkStatus.js';


const Home = () => {

  const { encoded_zoho_lead_id,encoded_interview_link_send_count } = useParams(); // Get encoded student_id from URL
  console.log("encoded_zoho_lead_id",encoded_zoho_lead_id)
  useInterviewLinkStatus(encoded_zoho_lead_id);

  // const InterviewLinkStatus = async (encoded_zoho_lead_id) => {
  //   if (!encoded_zoho_lead_id) {
  //       // console.error("No encoded_zoho_lead_id provided.",encoded_zoho_lead_id);
  //       return;
  //   }
  //   const formData = new FormData();
  //   formData.append("zoho_lead_id", encoded_zoho_lead_id);
  //   // console.log("Append zoh leader",encoded_zoho_lead_id)
  //   try {
  //       const response = await axios.post(
  //           `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-attend-status/`,
  //           formData
  //       );
  //       if (response.status === 200) {
  //         console.log("Starting exam...");
  //       } 
  //   } catch (error) {
  //     if (error.response && error.response.status === 410) {
  //       console.log("error.response.status",error.response.status);
  //       console.log("Interview link has expired. Please contact the administrator.");
  //       navigate("/expired");
  //   } else {
  //       console.log("An error occurred:", error);
  //       alert("An error occurred while checking the interview link status.");
  //   }
  //   }
  // }

  // useEffect(() => {
  //     InterviewLinkStatus(encoded_zoho_lead_id);
  // }, [encoded_zoho_lead_id]); // Runs when `encoded_zoho_lead_id` changes

    
  // console.log("encoded_interview_link_send_count: " + encoded_interview_link_send_count);

  return (
    <div className="bg-white">

      <div className="relative isolate px-6 pt-8 lg:px-8">
        <div
          aria-hidden="true"
          className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
        >
          <div
            style={{
              clipPath:
                "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)",
            }}
            className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
          />
        </div>
        <div className="mx-auto max-w-2xl py-12">
        <img src={Interview} alt="intervew Img" className="intrviewImg h-auto max-w-full"/>
          <div className="hidden sm:mb-8 sm:flex sm:justify-center">
          </div>
          <div className="text-center">
            <h1 className="text-balance text-4xl font-semibold tracking-tight text-gray-900 sm:text-5xl">
                AI-powered Interview Assistant
            </h1>
            <p className="mt-8 text-pretty text-lg font-medium text-gray-500 sm:text-xl/8">
            Our AI-powered platform helps you prepare for job interviews by simulating real-life scenarios, providing feedback, and enhancing your interview skills.

            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <NavLink 
                // to={`/terms-and-conditions/${student_id}`}
                to='/terms-and-conditions'
                state={{ encoded_zoho_lead_id,encoded_interview_link_send_count }}
                className="rounded-md bg-pink-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-pink-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Get started
              </NavLink>
              {/* <a href="#" className="text-sm/6 font-semibold text-gray-900">
                Learn more <span aria-hidden="true">→</span>
              </a> */}
            </div>
          </div>
        </div>
        <div
          aria-hidden="true"
          className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]"
        >
          <div
            style={{
              clipPath:
                "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)",
            }}
            className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]"
          />
        </div>
      </div>
    </div>
  );
};

export default Home;
