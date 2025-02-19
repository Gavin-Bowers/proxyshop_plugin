This is a plugin for [Proxyshop](https://github.com/Investigamer/Proxyshop)

# Showcase

<table>
  <tr>
      <th scope="row" colspan="5">Colors</th>
  </tr>
  <tr>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/37b3dae4-fba6-4bc4-8131-fb923666b2fa></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/1e74e24d-0ad1-48ca-a3c9-fb4e0c340fcc></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/60366998-ba3e-420c-b96c-41ff51dbfbd8></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/9c0e0963-6791-4f7d-b88e-d582b1c39706></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/da79d63c-05c0-4be6-b957-9a045c389a3b></td>
  </tr>
  <tr>
      <th scope="row" colspan="5">Devoid Colors</th>
  </tr>
  <tr>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/caae6e45-31d6-48a5-b618-25f27d6d87b1></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/c21f343a-7312-46ad-9e03-5a8d130ab6d5></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/ae14344c-a57d-4ac8-bf8d-c4928057d63f></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/5d0c5d1d-7ee3-4195-8738-0e85f80c20f5></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/dc1463f0-24f2-4cb4-ba1f-ab914750ce8a></td>
  </tr>
  <tr>
      <th scope="row" colspan="5">Artifact, Colorless, Multicolored, and Devoid Multicolored</th>
  </tr>
  <tr>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/a65f6fd6-187c-448a-bcc3-51ade830718c></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/26ac282a-6891-45e9-9487-8e412280b9e2></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/ec57dddc-9bb5-4fea-b24c-4e13ef259d01></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/0f6d4e1f-93d2-47ea-94fe-e6a9b2461cfe></td>
  </tr>
  <tr>
      <th scope="row" colspan="5">Hybrid Cards</th>
  </tr>
  <tr>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/bb56345d-f9e9-4f96-a7a0-58b802dc9329></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/a88280b8-bf19-432e-a5b6-60bbf49819d4></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/d8c6a695-9f80-4244-80a1-c5c5bd56d1e7></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/5dc90072-1e0f-4b75-9a95-f1464f3b25cc></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/59f1e44f-3dd8-4d46-8a42-a4e27e5b245f></td>
  </tr>
  <tr>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/a39b89e6-abab-4d8e-a72a-6b840099e79f></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/d855200a-ce64-4133-a004-6f62e9f4fc48></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/ebc39e64-a782-41c0-852b-6b8a4844722a></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/0e666cb4-33a0-47e2-a1d9-e231d897fa1d></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/0618cf1a-196f-4177-b831-05c1d44df2a4></td>
  </tr>
  <tr>
      <th scope="row" colspan="5">Sagas, Classes, and Planeswalkers</th>
  </tr>
  <tr>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/d2c0a913-56f2-4a6c-add7-4103335cefbc></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/fe58f681-24bc-491a-ab86-a4db6bd3e7f9></td>
    <td valign="top"><img align=top src= https://github.com/user-attachments/assets/66abb965-a6ce-41ae-bda8-9408fb3dc29e></td>

  </tr>
</table>

# Changelog

Updated for Proxyshop 1.14

1.14 refers to the code on the main branch, it hasn't been packaged for release yet

Settings now work!

The settings are configured to be as accurate as possible by default. However, the template has some differences from real cards for quality reasons.
* Textboxes are cropped in slightly to remove the bevel, and it's recreated in photoshop. This is to give more control and get cleaner lines
* The dual land textboxes were created by color grading the basic land textboxes to match the dual lands. This allows me to make dual lands programmatically
* The textboxes for artifact and blue cards are AI upscaled, since the results were so good, and they really benefitted from the added quality
* Colorless cards from MH3 are implemented as a filter for artifact cards. I did this for greater flexibility. I also changed the textbox color overlay to align with edges of the bevel. The overlay on the actual cards doesn't. I don't understand why they did it that way
* The pinline color for red lands is based on 7th edition while the others are from CMM, because the CMM mountain is weirdly desaturated
* I didn't include the old basic land watermarks. The watermarks added by Proxyshop are the modern ones which are different

# Feedback

If you have any issues or want any features to be added, let me know. My Discord handle is `gavin15` and my username is `[Gavin]`. I am open to contributions and collaboration.
