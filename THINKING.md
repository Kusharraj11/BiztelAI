# THINKING

## Understand the user

My assumption is that the supervisor controls the shift, assists workers with their concerns, and ensures that the tasks performed follow the correct protocol. Fast feedback is needed on issues regarding quality, maintenance, and safety. It may be provided over the phone.

Several PDFs will require a lot of time for searching. Different versions of the same PDF file may provide conflicting information. I would like to assist the supervisor in finding an answer and locating the source of information.

## User journey

1. Worker asks the supervisor about the issue, for example, machine alarm.
2. The supervisor starts the app on the smartphone and enters the question.
3. The app searches the PDF files and provides the answer with a source.
4. The supervisor views the version of the document and opens the PDF file if additional information is needed.
5. If there is no answer provided, the app tells that it cannot find it. The supervisor contacts the appropriate person instead of guessing.
6. If there is a need to compare the old procedure, the supervisor turns on the option to display old versions of documents.

There are possible issues that might occur: the question may be formulated incorrectly, the Wi-Fi connection may fail, the model may misinterpret the table, the old document may have outdated procedures. That is why I added sources, revision marks, loading messages, not-found messages.


## AI challenge


Firstly, I prompted AI what I want from my application: FastAPI server, React page, local Ollama, and answers based on provided PDFs. I told it to look through documents before deciding to use the RAG method and make things simple.

When developing my application, AI noted that there were contradictions in the revisions in the PDFs. Furthermore, testing revealed that the first model could not interpret the sampling tables correctly, while full-page retrieval was full of unnecessary data. Following this analysis, I replaced the model, used section retrieval, and applied revision filtering.

Later on, I prompted my local Ollama to analyze the user journey I have come up with as an overly cautious product manager and supervisor. It questioned connectivity, ambiguous questions, and trust in source links. I agreed with these claims but disagreed with the idea of adding safety overrides without verifying them with the customer.

This approach helped me concentrate on credible sources and current procedures.

## The improvement I added, and why

I also included revision-aware search. The normal queries will have access to the most current version of the document found within the provided PDF files. Previous revisions are only included if the user chooses the history feature.

In another instance, Rev 03 and Rev 04 have two distinct locations for waste material that is rejected. An incorrect location should not be given to the supervisor simply because that paragraph answered the query. The app provides revision indicators to help the user compare revisions if necessary. In a real-life scenario, this would link up to the approved document list in QMS.

## Final reflection

The major difficulty I faced was getting valid responses to my queries via a model on a local level. The initial version was able to respond to some basic queries, yet it had some troubles understanding sampling tables and provided incorrect descriptions of people's responsibilities. Having just a source hyperlink is not enough to validate the provided data.

The switch from Qwen2.5 3B to Qwen3 4B along with changing the way of providing evidence made the process more effective. Rather than extracting a complete page, the application now extracts numbered sections needed. It keeps continued sections and maintains information within tables. In case of an explicit lot size, the Python finds the required section of the PDF before sending it to the model.