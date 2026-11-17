// Creates this year's audience vote form ("Vote for the most popular film") in Google Forms.
//
// How to use (takes two minutes, in the Google account that should own the form):
//   1. Go to https://script.google.com and click "New project".
//   2. Delete what is there, paste this whole file, and click Run (the ▶ button).
//   3. Allow access when Google asks (the script only creates this one form in your Google Drive).
//   4. Open "Execution log" at the bottom: it shows the form's public link and its edit link.
//   5. Put the public link in site.json -> links.vote_form. The /vote/ page and its QR code then lead to it.
//
// Next year: change TITLE, FILMS (screening order, from festival.json) and SCREENINGS, then run it again.

const TITLE = "A World of Dark Comedy 7 - Voting";

const FILMS = [
    "Bite, or Bark",
    "The Inheritance",
    "Killing Time",
    "Just Men",
    "The Exterminator",
    "Lemon Squeezy",
    "Untouched",
    "Glory Hole",
    "Manus Erectus",
    "To Bind, or Not to Bind",
    "Uncle Artoo"
];

const SCREENINGS = [
    "Luna Cinema Leederville, Fri 4 Dec 2026",
    "Luna on SX, Fremantle, Fri 11 Dec 2026"
];

function createVoteForm() {
  const form = FormApp.create(TITLE);
  form.setDescription('Vote for the most popular film! Pick your favourite of the ' + FILMS.length +
                      ' films, in the order they were screened.');
  form.addMultipleChoiceItem()
      .setTitle('Which film was your favourite?')
      .setChoiceValues(FILMS.map((title, i) => (i + 1) + '. ' + title))
      .setRequired(true);
  form.addMultipleChoiceItem()
      .setTitle('Which screening were you at?')
      .setChoiceValues(SCREENINGS)
      .setRequired(false);
  form.addParagraphTextItem()
      .setTitle('Anything you would like to tell us about the films or the night?')
      .setRequired(false);
  form.setConfirmationMessage('Thanks for voting, and thanks for coming!');
  form.setShowLinkToRespondAgain(false);
  Logger.log('Public link (put this in site.json): ' + form.getPublishedUrl());
  Logger.log('Edit link (keep this for yourself):   ' + form.getEditUrl());
}
