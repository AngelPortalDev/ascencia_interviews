import React from "react";
import { useLocation, useNavigate, useParams, NavLink } from "react-router-dom";

const PrivacyPolicy = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const encoded_zoho_lead_id1 = location.state?.encoded_zoho_lead_id || null;
  const encoded_interview_link_send_count2 =
    location.state?.encoded_interview_link_send_count || null;


  const styles = {
    sectionstyle: {
      marginTop: "10px",
    },
    privacyPara: {
      marginTop: "6px",
    },
  };

 const gotoBack = () => {
  if (encoded_zoho_lead_id1 && encoded_interview_link_send_count2) {
    navigate("/terms-and-conditions", {
      state: {
        encoded_zoho_lead_id: encoded_zoho_lead_id1,
        encoded_interview_link_send_count: encoded_interview_link_send_count2,
      },
    });
  } else {
    navigate(-1); // fallback
  }
};



  return (
    <div>
      <div className="bg-white min-h-screen">
        <div className="relative isolate px-6 pt-0 lg:px-8">
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
          <div className="mx-auto max-w-4xl py-8 sm:py-12 lg:py-12">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 sm:text-3xl leading-tight">
                Privacy Policy
              </h1>
            </div>

            <div className="space-y-8 text-gray-700">
              <section style={styles.sectionstyle}>
                <p className="text-lg font-semibold text-blue-600 termsheading">
                  Terms
                </p>
                <p>
                  By accessing this web site, you are agreeing to be bound by
                  these web site Terms and Conditions of Use, applicable laws
                  and regulations and their compliance. If you disagree with any
                  of the stated terms and conditions, you are prohibited from
                  using or accessing this site. The materials contained in this
                  site are secured by relevant copyright and trade mark law.
                </p>
              </section>
              <section style={styles.sectionstyle}>
                <p className="text-lg font-semibold text-blue-600 termsheading">
                  Use License
                </p>
                <p>
                  Permission is allowed to temporarily download one duplicate of
                  the materials (data or programming) on Ascencia Malta site for
                  individual and non-business use only. This is the just a
                  permit of license and not an exchange of title, and under this
                  permit you may not:
                </p>
                <br />
                <ol className="list-decimal pl-5">
                  <li>Modify or copy the materials</li>
                  <li>
                    Use the materials for any commercial use, or for any public
                    presentation (business or non-business)
                  </li>
                  <li>
                    Attempt to decompile or rebuild any product or material
                    contained on Ascencia Malta site
                  </li>
                  <li>
                    Remove any copyright or other restrictive documentations
                    from the materials; or
                  </li>
                  <li>
                    Transfer the materials to someone else or even “mirror” the
                    materials on another server.
                  </li>
                </ol>
                <br />
                <p>
                  This permit might consequently be terminated if you disregard
                  any of these confinements and may be ended by Ascencia Malta
                  Group whenever deemed. After permit termination or when your
                  viewing permit is terminated, you must destroy any downloaded
                  materials in your ownership whether in electronic or printed
                  form.
                </p>
              </section>
              <section style={styles.sectionstyle}>
                <p className="text-lg font-semibold text-blue-600">
                  Disclaimer
                </p>
                <p>
                  The materials on Ascencia Malta site are given “as is”.
                  Ascencia Malta Group makes no guarantees, communicated or
                  suggested, and thus renounces and nullifies every single other
                  warranties, including without impediment, inferred guarantees
                  or states of merchantability, fitness for a specific reason,
                  or non-encroachment of licensed property or other infringement
                  of rights. Further, Ascencia Malta Group does not warrant or
                  make any representations concerning the precision, likely
                  results, or unwavering quality of the utilization of the
                  materials on its Internet site or generally identifying with
                  such materials or on any destinations connected to this
                  website.
                </p>
              </section>
              <section style={styles.sectionstyle}>
                <p className="text-lg font-semibold text-blue-600">
                  Constraints
                </p>
                <p>
                  In no occasion should Ascencia Malta Group or its suppliers
                  subject for any harms (counting, without constraint, harms for
                  loss of information or benefit, or because of business
                  interference,) emerging out of the utilization or
                  powerlessness to utilize the materials on Ascencia Malta
                  Internet webpage, regardless of the possibility that Ascencia
                  Malta Group or a Ascencia Malta Group approved agent has been
                  told orally or in written of the likelihood of such harm.
                  Since a few purviews don’t permit constraints on inferred
                  guarantees, or impediments of obligation for weighty or
                  coincidental harms, these confinements may not make a
                  difference to you.
                </p>
              </section>
              <section style={styles.sectionstyle}>
                <p className="text-lg font-semibold text-blue-600">
                  Amendments and Errata
                </p>
                <p>
                  The materials showing up on Ascencia Malta site could
                  incorporate typographical, or photographic mistakes. Ascencia
                  Malta Group does not warrant that any of the materials on its
                  site are exact, finished, or current. Ascencia Malta Group may
                  roll out improvements to the materials contained on its site
                  whenever without notification. Ascencia Malta Group does not,
                  then again, make any dedication to update the materials.
                </p>
              </section>
              <section style={styles.sectionstyle}>
                <p className="text-lg font-semibold text-blue-600">Links</p>
                <p>
                  Ascencia Malta Group has not checked on the majority of the
                  websites or links connected to its website and is not in
                  charge of the substance of any such connected webpage. The
                  incorporation of any connection does not infer support by
                  Ascencia Malta Group of the site. Utilization of any such
                  connected site is at the user’s own risk.
                </p>
              </section>
              <section style={styles.sectionstyle}>
                <p className="text-lg font-semibold text-blue-600">
                  Governing Law
                </p>
                <p>
                  The laws of Malta should administer any case identifying with
                  the Ascencia Malta site without respect to its contention of
                  law provisions. General Terms and Conditions applicable to Use
                  of a Web Site.
                </p>
              </section>
              <section style={styles.sectionstyle}>
                <p className="text-lg font-semibold text-blue-600">
                  Privacy Policy
                </p>
                <p style={styles.privacyPara}>
                  Your privacy is critical to us. Likewise, we have built up
                  this Policy with the end goal you should see how we gather,
                  utilize, impart and reveal and make utilization of individual
                  data. The following blueprints our privacy policy.
                </p>
                <p style={styles.privacyPara}>
                  Before or at the time of collecting personal information, we
                  will identify the purposes for which information is being
                  collected.
                </p>
                <p style={styles.privacyPara}>
                  We will gather and utilization of individual data singularly
                  with the target of satisfying those reasons indicated by us
                  and for other good purposes, unless we get the assent of the
                  individual concerned or as required by law.
                </p>
                <p style={styles.privacyPara}>
                  We will just hold individual data the length of essential for
                  the satisfaction of those reasons.
                </p>
                <p style={styles.privacyPara}>
                  We will gather individual data by legal and reasonable means
                  and, where fitting, with the information or assent of the
                  individual concerned.
                </p>
                <p style={styles.privacyPara}>
                  Personal information ought to be important to the reasons for
                  which it is to be utilized, and, to the degree essential for
                  those reasons, ought to be exact, finished, and updated.
                </p>
                <p style={styles.privacyPara}>
                  We will protect individual data by security shields against
                  misfortune or burglary, and also unapproved access,
                  divulgence, duplicating, use or alteration.
                </p>
                <p style={styles.privacyPara}>
                  We will promptly provide customers with access to our policies
                  and procedures for the administration of individual data.
                </p>
                <p style={styles.privacyPara}>
                  We are focused on leading our business as per these standards
                  with a specific end goal to guarantee that the privacy of
                  individual data is secure and maintained.
                </p>
              </section>
            </div>

            <div className="mt-10 flex items-center justify-center">
              <button
                onClick={gotoBack}
                className="rounded-md bg-pink-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-pink-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;
