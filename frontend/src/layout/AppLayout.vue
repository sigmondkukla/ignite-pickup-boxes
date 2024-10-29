<script setup>
import { computed, ref, watch } from 'vue';
import AppFooter from './AppFooter.vue';
import AppTopbar from './AppTopbar.vue';
</script>

<template>
    <div class="layout-wrapper">
        <app-topbar></app-topbar>
        <div class="layout-main-container">
            <div class="layout-main">
                <div>
                    <Panel header="Welcome (read me first!)" toggleable class="mb-3">
                        <p class="m-0"><strong>Welcome to the Ignite Pickup Boxes control panel!</strong></p>
                        <p class="m-0">
                            Not sure where to start? Here's a quick guide:
                        </p>
                        <ol style="list-style-type: decimal; margin: revert; padding: revert;">
                            <li>Open the <em>Makerspace Print Tracker</em> spreadsheet in a new tab</li>
                            <li>Mark the finished print <em>In Boxes</em> on the sheet</li>
                            <li>Copy the recipent's email address, and take note of the print number
                            </li>
                            <li>Click the
                                <Chip label="+ New" /> button below
                            </li>
                            <li>Type in the print number and paste the email address</li>
                            <li>Type in a box number or click
                                <Chip label="✨ Auto" />
                            </li>
                            <li>Click
                                <Chip label="Save" />
                            </li>
                            <li>Click the blue unlock button next to the newly created print to open its box
                            </li>
                            <li>Place the print in the opened box, and close the door</li>
                        </ol>
                        <p class="m-0">
                            This may seem like a lot of steps, but I wanted to be thorough in this
                            documentation.
                            It should only take a dozen seconds or so to complete each print delivery, and
                            I'll
                            remove or shrink this guide once everyone is comfortable with the process.
                        </p>
                        <p class="m-0">
                            Note that this software automatically sends the recipent an email allowing them
                            to
                            unlock their box. If they have trouble, you can unlock it for them by clicking
                            the
                            blue
                            unlock button next to their print.
                        </p>
                        <p class="m-0">
                            By default, the below data table is sorted by print number, but you can click
                            any
                            column
                            header to sort by that column instead. You can also search for a print number,
                            email, or
                            box number by typing in the search box above the table.
                        </p>
                        <p class="m-0">
                            If you have any questions or suggestions, please don't hesitate to reach out to
                            Sig
                            while the bugs are being worked out. Thanks for your help!
                        </p>
                    </Panel>
                </div>
                <router-view></router-view>
            </div>
            <app-footer></app-footer>
        </div>
        <div class="layout-mask animate-fadein"></div>
    </div>
    <Toast />
</template>
